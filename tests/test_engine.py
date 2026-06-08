import pytest


def test_init_default(engine):
	assert engine._initialized


def test_init_custom_config(soundobj_module):
	e = soundobj_module.Engine(soundobj_module.EngineConfig(channels=2, sampleRate=44100, noDevice=True))
	assert e._initialized


def test_init_no_auto_start(soundobj_module):
	e = soundobj_module.Engine(soundobj_module.EngineConfig(noAutoStart=True, noDevice=True))
	assert e._initialized


def test_volume_roundtrip(no_device_engine):
	no_device_engine.volume = 0.3
	assert no_device_engine.volume == pytest.approx(0.3)


def test_start_stop(engine):
	assert engine.start() is True
	assert engine.stop() is True


def test_channels_positive(engine):
	assert engine.channels > 0


def test_sample_rate_positive(engine):
	assert engine.sample_rate > 0


def test_time_in_milliseconds(no_device_engine):
	assert no_device_engine.time_in_milliseconds >= 0


def test_listener_count(no_device_engine):
	assert no_device_engine.listener_count >= 1


def test_find_closest_listener(no_device_engine):
	idx = no_device_engine.find_closest_listener(0.0, 0.0, 0.0)
	assert 0 <= idx < no_device_engine.listener_count


def test_listener_position_roundtrip(no_device_engine):
	no_device_engine.set_listener_position(0, 1.0, 2.0, 3.0)
	assert no_device_engine.get_listener_position(0) == pytest.approx((1.0, 2.0, 3.0))


def test_listener_direction_roundtrip(no_device_engine):
	no_device_engine.set_listener_direction(0, 0.0, 0.0, -1.0)
	assert no_device_engine.get_listener_direction(0) == pytest.approx((0.0, 0.0, -1.0))


def test_listener_velocity_roundtrip(no_device_engine):
	no_device_engine.set_listener_velocity(0, 1.0, 0.0, 0.0)
	assert no_device_engine.get_listener_velocity(0) == pytest.approx((1.0, 0.0, 0.0))


def test_listener_cone_roundtrip(no_device_engine):
	no_device_engine.set_listener_cone(0, 0.5, 1.5, 0.2)
	assert no_device_engine.get_listener_cone(0) == pytest.approx((0.5, 1.5, 0.2))


def test_listener_world_up_roundtrip(no_device_engine):
	no_device_engine.set_listener_world_up(0, 0.0, 1.0, 0.0)
	assert no_device_engine.get_listener_world_up(0) == pytest.approx((0.0, 1.0, 0.0))


def test_listener_enable_disable(no_device_engine):
	no_device_engine.set_listener_enabled(0, False)
	assert no_device_engine.is_listener_enabled(0) is False
	no_device_engine.set_listener_enabled(0, True)
	assert no_device_engine.is_listener_enabled(0) is True


def test_engine_play_sound(engine, wav_file):
	assert engine.play_sound(wav_file) is True


def test_module_play_sound(engine, wav_file):
	import soundobj
	assert soundobj.play_sound(wav_file) is True
