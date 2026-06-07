#include "url_vfs.h"
#include <curl/curl.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define URL_FILE_MAGIC  0x75726C66u
#define URL_BUFFER_SIZE (256 * 1024)
#define URL_READ_TIMEOUT_SECS 10L
#define LIVE_BUF_SIZE       (512 * 1024)
#define LIVE_HEADER_RESERVE (64 * 1024)  // keep this many bytes pinned at the start so decoders can re-read the container header
#define LIVE_PREBUFFER_SIZE (32 * 1024)  // fill at least this much before returning from open so the decoder has data to probe

static int s_curl_init_count = 0;

// All file handles are wrapped here so the VFS callbacks can tell URL handles from
// default-VFS handles without inspecting platform-specific types.
typedef struct {
	uint32_t magic;          // URL_FILE_MAGIC for URL files, 0 for default-VFS files
	ma_vfs_file inner;       // platform handle for non-URL files
	CURL* curl;
	char url[4096];
	ma_int64 position;
	ma_int64 content_length;
	unsigned char* buf;
	ma_int64 buf_start;
	size_t buf_len;
	int range_not_supported; // server returned 200 on a Range request, so seeking past the first buffer is impossible
	// Live stream fields. Only valid when is_live_stream == 1.
	int is_live_stream;
	CURLM* curl_multi;
	int transfer_active;
	int connection_closed;
	int curl_paused;
	unsigned char* live_buf;
	size_t live_bytes_buffered;
	ma_int64 live_window_start;  // absolute stream offset of live_buf[0]
	ma_int64 live_min_reachable; // earliest position ever sought to; compaction never advances past this
} vfs_file_handle;

typedef struct {
	unsigned char* data;
	size_t size;
	size_t cap;
} write_buf;

static int is_url_path(const char* path) {
	return strncmp(path, "http://", 7) == 0  ||
	       strncmp(path, "https://", 8) == 0 ||
	       strncmp(path, "ftp://", 6) == 0   ||
	       strncmp(path, "ftps://", 7) == 0;
}

static size_t curl_write_cb(char* ptr, size_t size, size_t nmemb, void* userdata) {
	write_buf* wb = (write_buf*)userdata;
	size_t n = size * nmemb;
	// Returning 0 aborts the transfer. The caller treats CURLE_WRITE_ERROR with partial
	// data as a successful capped read, so this is intentional.
	if (wb->size >= wb->cap) return 0;
	if (wb->size + n > wb->cap) n = wb->cap - wb->size;
	memcpy(wb->data + wb->size, ptr, n);
	wb->size += n;
	return size * nmemb;
}

// libcurl re-delivers the full chunk unchanged on resume, so doing a partial copy before
// returning CURL_WRITEFUNC_PAUSE would cause those bytes to be written twice. If there is
// no room, pause and let the buffer fully drain first.
static size_t live_write_cb(char* ptr, size_t size, size_t nmemb, void* userdata) {
	vfs_file_handle* h = (vfs_file_handle*)userdata;
	size_t chunk_size = size * nmemb;
	size_t space_remaining = LIVE_BUF_SIZE - h->live_bytes_buffered;
	if (chunk_size > space_remaining) {
		h->curl_paused = 1;
		return CURL_WRITEFUNC_PAUSE;
	}
	memcpy(h->live_buf + h->live_bytes_buffered, ptr, chunk_size);
	h->live_bytes_buffered += chunk_size;
	return chunk_size;
}

static void pump_live(vfs_file_handle* h, size_t target_bytes) {
	if (h->connection_closed) return;
	if (h->curl_paused && h->live_bytes_buffered < LIVE_BUF_SIZE) {
		curl_easy_pause(h->curl, CURLPAUSE_RECV_CONT);
		h->curl_paused = 0;
	}
	while (h->live_bytes_buffered < target_bytes && !h->connection_closed) {
		curl_multi_perform(h->curl_multi, &h->transfer_active);
		if (!h->transfer_active) {
			h->connection_closed = 1;
			break;
		}
		if (h->curl_paused) break;
		curl_multi_wait(h->curl_multi, NULL, 0, 50, NULL);
	}
}

static ma_result url_vfs_open(ma_vfs* pVFS, const char* pFilePath, ma_uint32 openMode, ma_vfs_file* pFile) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)calloc(1, sizeof(vfs_file_handle));
	if (!h) return MA_OUT_OF_MEMORY;
	if (!is_url_path(pFilePath)) {
		ma_result r = vfs->default_vfs.cb.onOpen((ma_vfs*)&vfs->default_vfs, pFilePath, openMode, &h->inner);
		if (r != MA_SUCCESS) { free(h); return r; }
		h->magic = 0;
		*pFile = h;
		return MA_SUCCESS;
	}
	h->magic = URL_FILE_MAGIC;
	strncpy(h->url, pFilePath, sizeof(h->url) - 1);
	h->content_length = -1;
	h->buf = (unsigned char*)malloc(URL_BUFFER_SIZE);
	if (!h->buf) { free(h); return MA_OUT_OF_MEMORY; }
	CURL* head = curl_easy_init();
	if (head) {
		curl_off_t len = -1;
		curl_easy_setopt(head, CURLOPT_URL, h->url);
		curl_easy_setopt(head, CURLOPT_NOBODY, 1L);
		curl_easy_setopt(head, CURLOPT_FOLLOWLOCATION, 1L);
		curl_easy_setopt(head, CURLOPT_TIMEOUT, 10L);
		if (curl_easy_perform(head) == CURLE_OK)
			curl_easy_getinfo(head, CURLINFO_CONTENT_LENGTH_DOWNLOAD_T, &len);
		if (len >= 0)
			h->content_length = (ma_int64)len;
		curl_easy_cleanup(head);
	}
	h->curl = curl_easy_init();
	if (!h->curl) { free(h->buf); free(h); return MA_ERROR; }
	// No Content-Length means either a live/radio stream or chunked transfer. Neither
	// supports range requests, so switch to a persistent connection with a sliding window.
	if (h->content_length < 0) {
		h->is_live_stream = 1;
		h->live_buf = (unsigned char*)malloc(LIVE_BUF_SIZE);
		if (!h->live_buf) {
			curl_easy_cleanup(h->curl);
			free(h->buf);
			free(h);
			return MA_OUT_OF_MEMORY;
		}
		h->curl_multi = curl_multi_init();
		if (!h->curl_multi) {
			free(h->live_buf);
			curl_easy_cleanup(h->curl);
			free(h->buf);
			free(h);
			return MA_ERROR;
		}
		h->transfer_active = 1;
		// Ogg/Opus decoders typically seek back to byte 0 after initial format detection to re-read the container header.
		h->live_min_reachable = LIVE_HEADER_RESERVE;
		curl_easy_setopt(h->curl, CURLOPT_URL, h->url);
		curl_easy_setopt(h->curl, CURLOPT_FOLLOWLOCATION, 1L);
		curl_easy_setopt(h->curl, CURLOPT_WRITEFUNCTION, live_write_cb);
		curl_easy_setopt(h->curl, CURLOPT_WRITEDATA, h);
		curl_multi_add_handle(h->curl_multi, h->curl);
		pump_live(h, LIVE_PREBUFFER_SIZE);
		if (h->connection_closed && h->live_bytes_buffered == 0) {
			curl_multi_remove_handle(h->curl_multi, h->curl);
			curl_multi_cleanup(h->curl_multi);
			free(h->live_buf);
			curl_easy_cleanup(h->curl);
			free(h->buf);
			free(h);
			*pFile = NULL;
			return MA_IO_ERROR;
		}
	}
	*pFile = h;
	return MA_SUCCESS;
}

static ma_result url_vfs_open_w(ma_vfs* pVFS, const wchar_t* pFilePath, ma_uint32 openMode, ma_vfs_file* pFile) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)calloc(1, sizeof(vfs_file_handle));
	if (!h) return MA_OUT_OF_MEMORY;
	ma_result r = vfs->default_vfs.cb.onOpenW((ma_vfs*)&vfs->default_vfs, pFilePath, openMode, &h->inner);
	if (r != MA_SUCCESS) { free(h); return r; }
	h->magic = 0;
	*pFile = h;
	return MA_SUCCESS;
}

static ma_result url_vfs_close(ma_vfs* pVFS, ma_vfs_file file) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)file;
	if (h->magic != URL_FILE_MAGIC) {
		ma_result r = vfs->default_vfs.cb.onClose((ma_vfs*)&vfs->default_vfs, h->inner);
		free(h);
		return r;
	}
	if (h->is_live_stream) {
		curl_multi_remove_handle(h->curl_multi, h->curl);
		curl_multi_cleanup(h->curl_multi);
		free(h->live_buf);
	}
	curl_easy_cleanup(h->curl);
	free(h->buf);
	free(h);
	return MA_SUCCESS;
}

static ma_result url_vfs_read(ma_vfs* pVFS, ma_vfs_file file, void* pDst, size_t sizeInBytes, size_t* pBytesRead) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)file;
	if (h->magic != URL_FILE_MAGIC)
		return vfs->default_vfs.cb.onRead((ma_vfs*)&vfs->default_vfs, h->inner, pDst, sizeInBytes, pBytesRead);
	if (pBytesRead) *pBytesRead = 0;
	if (h->is_live_stream) {
		size_t read_offset = (size_t)(h->position - h->live_window_start);
		// Slide the window forward to reclaim buffer space. Keep everything from
		// live_min_reachable forward since the decoder might seek back there.
		ma_int64 compaction_limit = h->position - (ma_int64)(LIVE_BUF_SIZE / 2);
		if (compaction_limit < h->live_min_reachable) compaction_limit = h->live_min_reachable;
		if (compaction_limit < h->live_window_start)  compaction_limit = h->live_window_start;
		if (compaction_limit > h->live_window_start) {
			size_t bytes_to_drop = (size_t)(compaction_limit - h->live_window_start);
			memmove(h->live_buf, h->live_buf + bytes_to_drop, h->live_bytes_buffered - bytes_to_drop);
			h->live_bytes_buffered -= bytes_to_drop;
			h->live_window_start = compaction_limit;
			read_offset -= bytes_to_drop;
		}
		size_t target_fill = read_offset + sizeInBytes;
		if (target_fill > LIVE_BUF_SIZE) target_fill = LIVE_BUF_SIZE;
		pump_live(h, target_fill);
		size_t available = h->live_bytes_buffered - read_offset;
		if (available == 0)
			return h->connection_closed ? MA_AT_END : MA_IO_ERROR;
		size_t n = available < sizeInBytes ? available : sizeInBytes;
		memcpy(pDst, h->live_buf + read_offset, n);
		h->position += (ma_int64)n;
		if (pBytesRead) *pBytesRead = n;
		return MA_SUCCESS;
	}
	if (h->content_length >= 0 && h->position >= h->content_length)
		return MA_AT_END;
	if (h->buf_len > 0 && h->position >= h->buf_start &&
	    h->position < (ma_int64)(h->buf_start + (ma_int64)h->buf_len)) {
		size_t offset = (size_t)(h->position - h->buf_start);
		size_t avail = h->buf_len - offset;
		size_t n = avail < sizeInBytes ? avail : sizeInBytes;
		memcpy(pDst, h->buf + offset, n);
		h->position += (ma_int64)n;
		if (pBytesRead) *pBytesRead = n;
		return MA_SUCCESS;
	}
	// If the server ignored the Range header we cannot seek, so fetching more data would
	// return bytes from position 0 rather than from h->position.
	if (h->range_not_supported) return MA_IO_ERROR;
	char range[64];
	ma_int64 end = h->position + URL_BUFFER_SIZE - 1;
	if (h->content_length > 0 && end >= h->content_length)
		end = h->content_length - 1;
	snprintf(range, sizeof(range), "%lld-%lld", (long long)h->position, (long long)end);
	write_buf wb = {0};
	wb.data = (unsigned char*)malloc(URL_BUFFER_SIZE);
	if (!wb.data) return MA_OUT_OF_MEMORY;
	wb.cap = URL_BUFFER_SIZE;
	curl_easy_reset(h->curl);
	curl_easy_setopt(h->curl, CURLOPT_URL, h->url);
	curl_easy_setopt(h->curl, CURLOPT_RANGE, range);
	curl_easy_setopt(h->curl, CURLOPT_WRITEFUNCTION, curl_write_cb);
	curl_easy_setopt(h->curl, CURLOPT_WRITEDATA, &wb);
	curl_easy_setopt(h->curl, CURLOPT_FOLLOWLOCATION, 1L);
	curl_easy_setopt(h->curl, CURLOPT_TIMEOUT, URL_READ_TIMEOUT_SECS);
	CURLcode rc = curl_easy_perform(h->curl);
	int have_data = (rc == CURLE_OK)
		|| (rc == CURLE_WRITE_ERROR && wb.size > 0)
		|| (rc == CURLE_OPERATION_TIMEDOUT && wb.size > 0);
	if (!have_data) {
		free(wb.data);
		return MA_IO_ERROR;
	}
	if (wb.size == 0) {
		free(wb.data);
		return MA_AT_END;
	}
	// A 200 response to a Range request means the server silently ignored the header.
	// Mark this so future cache misses fail immediately rather than returning wrong data.
	{
		long response_code = 0;
		curl_easy_getinfo(h->curl, CURLINFO_RESPONSE_CODE, &response_code);
		if (response_code == 200) h->range_not_supported = 1;
	}
	free(h->buf);
	h->buf = wb.data;
	h->buf_start = h->position;
	h->buf_len = wb.size;
	size_t n = wb.size < sizeInBytes ? wb.size : sizeInBytes;
	memcpy(pDst, h->buf, n);
	h->position += (ma_int64)n;
	if (pBytesRead) *pBytesRead = n;
	return MA_SUCCESS;
}

static ma_result url_vfs_write(ma_vfs* pVFS, ma_vfs_file file, const void* pSrc, size_t sizeInBytes, size_t* pBytesWritten) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)file;
	if (h->magic != URL_FILE_MAGIC)
		return vfs->default_vfs.cb.onWrite((ma_vfs*)&vfs->default_vfs, h->inner, pSrc, sizeInBytes, pBytesWritten);
	return MA_NOT_IMPLEMENTED;
}

static ma_result url_vfs_seek(ma_vfs* pVFS, ma_vfs_file file, ma_int64 offset, ma_seek_origin origin) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)file;
	if (h->magic != URL_FILE_MAGIC)
		return vfs->default_vfs.cb.onSeek((ma_vfs*)&vfs->default_vfs, h->inner, offset, origin);
	ma_int64 new_pos;
	switch (origin) {
		case ma_seek_origin_start:   new_pos = offset; break;
		case ma_seek_origin_current: new_pos = h->position + offset; break;
		case ma_seek_origin_end:
			if (h->content_length < 0) return MA_ERROR;
			new_pos = h->content_length + offset;
			break;
		default: return MA_INVALID_ARGS;
	}
	if (new_pos < 0) new_pos = 0;
	if (h->is_live_stream) {
		// We can only honor seeks within what is currently buffered. Use MA_NOT_IMPLEMENTED here rather than MA_ERROR
		// because nothing is broken, the position is just unavailable.
		if (new_pos < h->live_window_start ||
		    new_pos >= (ma_int64)(h->live_window_start + h->live_bytes_buffered))
			return MA_NOT_IMPLEMENTED;
		// Track the earliest seek so compaction never discards data the decoder might need again.
		if (new_pos < h->live_min_reachable)
			h->live_min_reachable = new_pos;
		h->position = new_pos;
		return MA_SUCCESS;
	}
	// For finite files on Range-unsupported servers, the initial fetch holds the entire file.
	// Never invalidate the buffer, just move the cursor. The read path returns MA_AT_END
	// once position reaches content_length.
	if (h->range_not_supported && h->content_length >= 0) {
		h->position = new_pos;
		return MA_SUCCESS;
	}
	if (h->buf_len > 0 && new_pos >= h->buf_start &&
	    new_pos < (ma_int64)(h->buf_start + (ma_int64)h->buf_len)) {
		h->position = new_pos;
		return MA_SUCCESS;
	}
	h->buf_len = 0;
	h->buf_start = new_pos;
	h->position = new_pos;
	return MA_SUCCESS;
}

static ma_result url_vfs_tell(ma_vfs* pVFS, ma_vfs_file file, ma_int64* pCursor) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)file;
	if (h->magic != URL_FILE_MAGIC)
		return vfs->default_vfs.cb.onTell((ma_vfs*)&vfs->default_vfs, h->inner, pCursor);
	*pCursor = h->position;
	return MA_SUCCESS;
}

static ma_result url_vfs_info(ma_vfs* pVFS, ma_vfs_file file, ma_file_info* pInfo) {
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)pVFS;
	vfs_file_handle* h = (vfs_file_handle*)file;
	if (h->magic != URL_FILE_MAGIC)
		return vfs->default_vfs.cb.onInfo((ma_vfs*)&vfs->default_vfs, h->inner, pInfo);
	if (h->content_length < 0) {
		pInfo->sizeInBytes = 0;
		return MA_NOT_IMPLEMENTED;
	}
	pInfo->sizeInBytes = (ma_uint64)h->content_length;
	return MA_SUCCESS;
}

ma_vfs* soundobj_url_vfs_create(void) {
	if (s_curl_init_count++ == 0)
		curl_global_init(CURL_GLOBAL_DEFAULT);
	soundobj_url_vfs* vfs = (soundobj_url_vfs*)calloc(1, sizeof(soundobj_url_vfs));
	if (!vfs) return NULL;
	ma_default_vfs_init(&vfs->default_vfs, NULL);
	vfs->cb.onOpen  = url_vfs_open;
	vfs->cb.onOpenW = url_vfs_open_w;
	vfs->cb.onClose = url_vfs_close;
	vfs->cb.onRead  = url_vfs_read;
	vfs->cb.onWrite = url_vfs_write;
	vfs->cb.onSeek  = url_vfs_seek;
	vfs->cb.onTell  = url_vfs_tell;
	vfs->cb.onInfo  = url_vfs_info;
	return (ma_vfs*)vfs;
}

void soundobj_url_vfs_destroy(ma_vfs* vfs) {
	if (!vfs) return;
	// ma_default_vfs initialized with NULL allocator has no heap state to free
	free(vfs);
	if (--s_curl_init_count == 0)
		curl_global_cleanup();
}
