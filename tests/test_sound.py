import pytest


def test_load_stream_false(no_device_engine, audio_file):
	import soundobj
	s = soundobj.Sound(no_device_engine)
	assert s.load(audio_file, stream=False) is True
	assert s._loaded is True


def test_load_stream_true(engine, audio_file):
	import soundobj
	s = soundobj.Sound(engine)
	assert s.load(audio_file, stream=True) is True
	assert s._loaded is True


def test_length_in_seconds(loaded_sound):
	assert loaded_sound.length_in_seconds > 0


def test_play_returns_true(loaded_sound_real):
	assert loaded_sound_real.play() is True


def test_is_playing_after_play(loaded_sound_real):
	loaded_sound_real.play()
	assert loaded_sound_real.is_playing is True


def test_pause_stops_playback(loaded_sound_real):
	loaded_sound_real.play()
	loaded_sound_real.pause()
	assert loaded_sound_real.is_playing is False


def test_stop(loaded_sound_real):
	loaded_sound_real.play()
	assert loaded_sound_real.stop() is True


def test_fade_in(loaded_sound_real):
	assert loaded_sound_real.fade_in(100) is True


def test_fade_out(loaded_sound_real):
	loaded_sound_real.play()
	assert loaded_sound_real.fade_out(100) is True


def test_volume_roundtrip(loaded_sound):
	loaded_sound.volume = 0.3
	assert loaded_sound.volume == pytest.approx(0.3)


def test_pitch_roundtrip(loaded_sound):
	loaded_sound.pitch = 1.5
	assert loaded_sound.pitch == pytest.approx(1.5)


def test_pan_roundtrip(loaded_sound):
	loaded_sound.pan = -0.5
	assert loaded_sound.pan == pytest.approx(-0.5)


def test_looping_roundtrip(loaded_sound):
	loaded_sound.looping = True
	assert loaded_sound.looping is True
	loaded_sound.looping = False
	assert loaded_sound.looping is False


def test_seek_and_position(loaded_sound_real):
	loaded_sound_real.play()
	loaded_sound_real.pause()
	target = loaded_sound_real.length_in_seconds * 0.5
	loaded_sound_real.position_in_seconds = target
	assert loaded_sound_real.position_in_seconds == pytest.approx(target, abs=0.1)


def test_position_3d_roundtrip(loaded_sound):
	loaded_sound.position = (1.0, 2.0, 3.0)
	assert loaded_sound.position == pytest.approx((1.0, 2.0, 3.0))


def test_direction_roundtrip(loaded_sound):
	loaded_sound.direction = (0.0, 0.0, -1.0)
	assert loaded_sound.direction == pytest.approx((0.0, 0.0, -1.0))


def test_velocity_roundtrip(loaded_sound):
	loaded_sound.velocity = (1.0, 0.0, 0.0)
	assert loaded_sound.velocity == pytest.approx((1.0, 0.0, 0.0))


def test_spatialization_enabled_roundtrip(loaded_sound):
	loaded_sound.spatialization_enabled = False
	assert loaded_sound.spatialization_enabled is False
	loaded_sound.spatialization_enabled = True
	assert loaded_sound.spatialization_enabled is True


def test_rolloff_roundtrip(loaded_sound):
	loaded_sound.rolloff = 2.0
	assert loaded_sound.rolloff == pytest.approx(2.0)


def test_min_distance_roundtrip(loaded_sound):
	loaded_sound.min_distance = 5.0
	assert loaded_sound.min_distance == pytest.approx(5.0)


def test_max_distance_roundtrip(loaded_sound):
	loaded_sound.max_distance = 500.0
	assert loaded_sound.max_distance == pytest.approx(500.0)


def test_min_gain_roundtrip(loaded_sound):
	loaded_sound.min_gain = 0.1
	assert loaded_sound.min_gain == pytest.approx(0.1)


def test_max_gain_roundtrip(loaded_sound):
	loaded_sound.max_gain = 0.9
	assert loaded_sound.max_gain == pytest.approx(0.9)


def test_cone_roundtrip(loaded_sound):
	loaded_sound.cone = (0.5, 1.5, 0.2)
	assert loaded_sound.cone == pytest.approx((0.5, 1.5, 0.2))


def test_doppler_factor_roundtrip(loaded_sound):
	loaded_sound.doppler_factor = 0.5
	assert loaded_sound.doppler_factor == pytest.approx(0.5)


def test_directional_attenuation_factor_roundtrip(loaded_sound):
	loaded_sound.directional_attenuation_factor = 0.7
	assert loaded_sound.directional_attenuation_factor == pytest.approx(0.7)


def test_pinned_listener_index_roundtrip(loaded_sound):
	loaded_sound.pinned_listener_index = 0
	assert loaded_sound.pinned_listener_index == 0


def test_listener_index_readable(loaded_sound):
	assert isinstance(loaded_sound.listener_index, int)


def test_direction_to_listener_readable(loaded_sound):
	d = loaded_sound.direction_to_listener
	assert len(d) == 3
	assert all(isinstance(v, float) for v in d)


def test_attenuation_model_enum(loaded_sound):
	import soundobj
	for model in soundobj.AttenuationModel:
		loaded_sound.attenuation_model = model
		assert loaded_sound.attenuation_model == model


def test_attenuation_model_string(loaded_sound):
	import soundobj
	loaded_sound.attenuation_model = 'linear'
	assert loaded_sound.attenuation_model == soundobj.AttenuationModel.LINEAR


def test_positioning_mode_enum(loaded_sound):
	import soundobj
	loaded_sound.positioning = soundobj.PositioningMode.RELATIVE
	assert loaded_sound.positioning == soundobj.PositioningMode.RELATIVE


def test_positioning_mode_string(loaded_sound):
	import soundobj
	loaded_sound.positioning = 'relative'
	assert loaded_sound.positioning == soundobj.PositioningMode.RELATIVE


def test_unloaded_guards(no_device_engine):
	import soundobj
	s = soundobj.Sound(no_device_engine)
	assert s.play() is False
	assert s.volume == pytest.approx(0.0)
	assert s.pitch == pytest.approx(1.0)
	assert s.pan == pytest.approx(0.0)
	assert s.length_in_seconds == pytest.approx(0.0)
	assert s.is_playing is False
	assert s.looping is False


def test_load_nonexistent_file_raises(no_device_engine):
	import soundobj
	s = soundobj.Sound(no_device_engine)
	with pytest.raises(soundobj.MiniAudioError):
		s.load_from_file("/nonexistent/path/audio.wav")


def test_load_from_memory_raises(no_device_engine):
	import soundobj
	s = soundobj.Sound(no_device_engine)
	with pytest.raises(NotImplementedError):
		s.load_from_memory(b"\x00" * 100)


def test_sound_without_engine_uses_global(soundobj_module, wav_file):
	s = soundobj_module.Sound(source=wav_file)
	assert s._loaded is True


def test_double_load_same_instance(no_device_engine, wav_file):
	import soundobj
	s = soundobj.Sound(no_device_engine)
	s.load(wav_file, stream=False)
	s.load(wav_file, stream=False)
	assert s._loaded is True
