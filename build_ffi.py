import os
import sys
from pathlib import Path
from cffi import FFI

# Use the directory containing this script as the root for path resolutions
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
	sys.path.append(str(root_dir))

import vcpkg
lib_dir = root_dir / "lib"

if not vcpkg.install_path.exists():
	vcpkg.build()
ffibuilder = FFI()

with open(root_dir / "declarations.h", "r") as f:
	cdefs = f.read()
ffibuilder.cdef(cdefs)

include_dirs = [str(root_dir), str(lib_dir), str(vcpkg.install_path / "include")]
library_dirs = [str(vcpkg.install_path / "lib")]

common_libs = ["opus", "opusfile", "ogg", "vorbis", "vorbisfile"]
if sys.platform == "win32":
	libraries = common_libs + ["libcurl", "zlib", "ws2_32", "crypt32", "wldap32", "advapi32", "secur32", "iphlpapi", "normaliz"]
	extra_link_args = []
elif sys.platform == "darwin":
	libraries = common_libs + ["curl", "ssl", "crypto", "z"]
	extra_link_args = []
else:
	libraries = common_libs + ["curl", "ssl", "crypto", "z"]
	extra_link_args = []

ffibuilder.set_source("_c_miniaudio", """
	#include <stdint.h>
	#include <stdlib.h>
	#define MINIAUDIO_IMPLEMENTATION
	#include "lib/miniaudio.h"
	#include "lib/miniaudio_libopus.h"
	#include "lib/miniaudio_libvorbis.h"

	// Include implementation files directly to avoid complex linking issues during pip install
	#include "lib/miniaudio_libopus.c"
	#include "lib/miniaudio_libvorbis.c"
	#include <curl/curl.h>
	#include "lib/url_vfs.c"

	ma_decoding_backend_vtable** soundobj_get_custom_decoders(ma_uint32* count) {
		static ma_decoding_backend_vtable* custom_decoders[2];
		custom_decoders[0] = ma_decoding_backend_libvorbis;
		custom_decoders[1] = ma_decoding_backend_libopus;
		if (count) *count = sizeof(custom_decoders) / sizeof(custom_decoders[0]);
		return custom_decoders;
	}
""",
	include_dirs=include_dirs,
	library_dirs=library_dirs,
	libraries=libraries,
	extra_link_args=extra_link_args,
)

if __name__ == "__main__":
	ffibuilder.compile(verbose=True)
