from pathlib import Path

import pytest

try:
	import soundobj
	_import_error = None
except Exception as e:
	soundobj = None
	_import_error = e

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def soundobj_module():
	if _import_error is not None:
		pytest.skip(f"soundobj unavailable: {_import_error}")
	return soundobj


@pytest.fixture(scope="session")
def wav_file():
	return str(FIXTURES / "test.wav")


@pytest.fixture(scope="session")
def ogg_file():
	return str(FIXTURES / "test.ogg")


@pytest.fixture(scope="session")
def opus_file():
	return str(FIXTURES / "test.opus")


@pytest.fixture(params=["wav_file", "ogg_file", "opus_file"])
def audio_file(request):
	return request.getfixturevalue(request.param)


@pytest.fixture(params=["wav_file", "ogg_file", "opus_file"])
def loaded_sound(request, no_device_engine):
	path = request.getfixturevalue(request.param)
	s = soundobj.Sound(no_device_engine)
	s.load(path, stream=False)
	yield s
	s.stop()


@pytest.fixture(params=["wav_file", "ogg_file", "opus_file"])
def loaded_sound_real(request, engine):
	path = request.getfixturevalue(request.param)
	s = soundobj.Sound(engine)
	s.load(path, stream=False)
	yield s
	s.stop()


@pytest.fixture
def engine():
	if _import_error is not None:
		pytest.skip(f"soundobj unavailable: {_import_error}")
	try:
		eng = soundobj.Engine()
	except soundobj.MiniAudioError as e:
		pytest.skip(f"no audio device: {e}")
	yield eng
	eng.stop()


@pytest.fixture
def no_device_engine():
	if _import_error is not None:
		pytest.skip(f"soundobj unavailable: {_import_error}")
	eng = soundobj.Engine(soundobj.EngineConfig(noDevice=True))
	yield eng
	eng.stop()
