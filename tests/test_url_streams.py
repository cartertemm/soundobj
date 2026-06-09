from pathlib import Path
import threading
import http.server
import time

import pytest
import soundobj

REPO_ROOT = Path(__file__).parent.parent
ITEM_OGG = str(REPO_ROOT / "item.ogg")


def test_local_file_still_loads():
	"""Regression: custom VFS must not break local file loading."""
	engine = soundobj.Engine()
	s = soundobj.Sound(engine)
	result = s.load(ITEM_OGG, stream=False)
	assert result is True
	assert s._loaded is True


def test_invalid_scheme_raises():
	engine = soundobj.Engine()
	s = soundobj.Sound(engine)
	with pytest.raises(ValueError, match="Unsupported URL scheme"):
		s.load_from_url("sftp://example.com/audio.ogg")


PORT = 18765


class _DirectoryHandler(http.server.SimpleHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

	def log_message(self, format, *args):
		pass


@pytest.fixture(scope="module")
def http_server():
	server = http.server.HTTPServer(("127.0.0.1", PORT), _DirectoryHandler)
	t = threading.Thread(target=server.serve_forever, daemon=True)
	t.start()
	yield f"http://127.0.0.1:{PORT}"
	server.shutdown()


def test_load_url_stream_true(http_server):
	"""stream=True: sound loads successfully."""
	engine = soundobj.Engine()
	s = soundobj.Sound(engine)
	result = s.load(f"{http_server}/item.ogg", stream=True)
	assert result is True
	assert s._loaded is True


def test_load_url_stream_false(http_server):
	"""stream=False: full decode into memory before playback."""
	engine = soundobj.Engine()
	s = soundobj.Sound(engine)
	result = s.load(f"{http_server}/item.ogg", stream=False)
	assert result is True
	assert s._loaded is True
	assert s.length_in_seconds > 0


def test_load_url_via_sound_constructor(http_server):
	"""URL passed directly to Sound() constructor."""
	engine = soundobj.Engine()
	s = soundobj.Sound(engine, source=f"{http_server}/item.ogg")
	assert s._loaded is True


def test_url_play_and_seek(http_server):
	"""Play briefly, seek to midpoint, confirm position updated."""
	engine = soundobj.Engine()
	s = soundobj.Sound(engine, source=f"{http_server}/item.ogg")
	assert s._loaded is True
	seek_target = s.length_in_seconds * 0.5
	s.play()
	time.sleep(0.05)
	s.position_in_seconds = seek_target
	time.sleep(0.2)
	assert s.position_in_seconds >= seek_target * 0.9
	s.stop()


def test_engine_double_init():
	"""Two Engine instances created and destroyed must not crash."""
	e1 = soundobj.Engine()
	del e1
	e2 = soundobj.Engine()
	s = soundobj.Sound(e2)
	result = s.load(ITEM_OGG, stream=False)
	assert result is True
	del e2
