from typing import Optional, Union
from dataclasses import dataclass
from enum import Enum
from _c_miniaudio import ffi, lib


class AttenuationModel(Enum):
	"""Attenuation models for distance-based volume falloff."""
	NONE = 'none'
	INVERSE = 'inverse'
	LINEAR = 'linear'
	EXPONENTIAL = 'exponential'


class PositioningMode(Enum):
	"""Positioning modes for sound sources."""
	ABSOLUTE = 'absolute'
	RELATIVE = 'relative'


# Global mapping dictionaries
ATTENUATION_MODEL_MAP = {
	AttenuationModel.NONE: lib.ma_attenuation_model_none,
	AttenuationModel.INVERSE: lib.ma_attenuation_model_inverse,
	AttenuationModel.LINEAR: lib.ma_attenuation_model_linear,
	AttenuationModel.EXPONENTIAL: lib.ma_attenuation_model_exponential
}

ATTENUATION_MODEL_REVERSE_MAP = {v:k for v, k in ATTENUATION_MODEL_MAP.items()}

POSITIONING_MODE_MAP = {
	PositioningMode.ABSOLUTE: lib.ma_positioning_absolute,
	PositioningMode.RELATIVE: lib.ma_positioning_relative
}

POSITIONING_MODE_REVERSE_MAP = {v:k for k, v in POSITIONING_MODE_MAP.items()}


def is_uri(x):
	"""Determines whether `x` is a URL.
	Args:
		x: String to check for URL format.
	Returns:
		True if x appears to be a URL, False otherwise.
	Note:
		This function uses basic URL parsing to detect URLs.
		It checks for the presence of both scheme and netloc components.
	"""
	# source: https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
	from urllib.parse import urlparse
	try:
		result = urlparse(x)
		return all([result.scheme, result.netloc])
	except AttributeError:
		return False


class MiniAudioError(Exception):
	"""Exception raised for miniaudio-related errors.
	This exception is raised when miniaudio operations fail, such as
	engine initialization, sound loading, or playback errors.
	"""
	pass


@dataclass
class EngineConfig:
	"""Configuration options for the audio engine.
	This class provides configuration options for initializing the audio engine.
	All parameters are optional and will use sensible defaults if not specified.
	Attributes:
		listenerCount: Number of 3D audio listeners (0 = use default).
		channels: Number of output channels (0 = use default, typically 2 for stereo).
		sampleRate: Sample rate in Hz (0 = use default, typically 44100 or 48000).
		periodSizeInFrames: Period size in frames (0 = use default).
		periodSizeInMilliseconds: Period size in milliseconds (0 = use default).
		gainSmoothTimeInFrames: Gain smoothing time in frames (0 = use default).
		gainSmoothTimeInMilliseconds: Gain smoothing time in milliseconds (0 = use default).
		defaultVolumeSmoothTimeInPCMFrames: Default volume smoothing time in PCM frames (0 = use default).
		preMixStackSizeInBytes: Pre-mix stack size in bytes (0 = use default).
		noAutoStart: If True, don't automatically start the engine after initialization.
		noDevice: If True, initialize without an audio device (for offline processing).
	"""
	listenerCount: int = 0
	channels: int = 0
	sampleRate: int = 0
	periodSizeInFrames: int = 0
	periodSizeInMilliseconds: int = 0
	gainSmoothTimeInFrames: int = 0
	gainSmoothTimeInMilliseconds: int = 0
	defaultVolumeSmoothTimeInPCMFrames: int = 0
	preMixStackSizeInBytes: int = 0
	noAutoStart: bool = False
	noDevice: bool = False


class Engine:
	"""Audio engine for managing sound playback and processing.
	The Engine class provides a high-level interface for audio operations,
	including sound loading, playback, and 3D audio processing. It wraps
	the miniaudio engine and provides a Pythonic interface.
	Args:
		config: Optional EngineConfig object for engine configuration.
			If None, uses default configuration.
	Attributes:
		_engine: FFI pointer to the underlying miniaudio engine.
		_config: Configuration used to initialize the engine.
		_initialized: Whether the engine has been successfully initialized.
	"""
	def __init__(self, config: Optional[EngineConfig] = None):
		self._engine = ffi.new("ma_engine*")
		self._resource_manager = ffi.new("ma_resource_manager*")
		self._config = config
		self._initialized = False
		ma_config = lib.ma_engine_config_init()
		if config:
			if config.channels > 0:
				ma_config.channels = config.channels
			if config.sampleRate > 0:
				ma_config.sampleRate = config.sampleRate
			if config.periodSizeInFrames > 0:
				ma_config.periodSizeInFrames = config.periodSizeInFrames
			if config.periodSizeInMilliseconds > 0:
				ma_config.periodSizeInMilliseconds = config.periodSizeInMilliseconds
			if config.listenerCount > 0:
				ma_config.listenerCount = config.listenerCount
			if config.noAutoStart:
				ma_config.noAutoStart = 1
			if config.noDevice:
				ma_config.noDevice = 1
		rm_config = lib.ma_resource_manager_config_init()
		if rm_config:
			rm_config.ppCustomDecodingBackendVTables = lib.soundobj_get_custom_decoders(ffi.addressof(rm_config, "customDecodingBackendCount"))
			result = lib.ma_resource_manager_init(ffi.addressof(rm_config), self._resource_manager)
			if result == lib.MA_SUCCESS:
				ma_config.pResourceManager = self._resource_manager
			else:
				self._resource_manager = ffi.NULL # if fail it's not game over, just custom formats won't be available. Maybe log somewhere if ma_log doesn't do enough?
		result = lib.ma_engine_init(ffi.addressof(ma_config), self._engine)
		if result != lib.MA_SUCCESS:
			raise MiniAudioError(f"Failed to initialize engine: {result}")
		self._initialized = True
	def __del__(self):
		"""Cleanup the engine when the object is destroyed."""
		if hasattr(self, '_initialized') and self._initialized:
			lib.ma_engine_uninit(self._engine)
			if self._resource_manager:
				lib.ma_resource_manager_uninit(self._resource_manager)
	def start(self) -> bool:
		"""Start the audio engine.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		result = lib.ma_engine_start(self._engine)
		return result == lib.MA_SUCCESS
	def stop(self) -> bool:
		"""Stop the audio engine.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		result = lib.ma_engine_stop(self._engine)
		return result == lib.MA_SUCCESS
	@property
	def volume(self) -> float:
		"""Get the master volume of the engine.
		Returns:
			Volume level as a float (0.0 to 1.0+).
		"""
		if not self._initialized:
			return 0.0
		return lib.ma_engine_get_volume(self._engine)
	@volume.setter
	def volume(self, value: float):
		"""Set the master volume of the engine.
		Args:
			value: Volume level as a float (0.0 to 1.0+).
		"""
		if not self._initialized:
			return
		lib.ma_engine_set_volume(self._engine, value)
	@property
	def channels(self) -> int:
		"""Get the number of output channels.
		Returns:
			Number of channels.
		"""
		if not self._initialized:
			return 0
		return lib.ma_engine_get_channels(self._engine)
	@property
	def sample_rate(self) -> int:
		"""Get the sample rate of the engine.
		Returns:
			Sample rate in Hz.
		"""
		if not self._initialized:
			return 0
		return lib.ma_engine_get_sample_rate(self._engine)
	@property
	def time_in_milliseconds(self) -> int:
		"""Get the current time in milliseconds.
		Returns:
			Time in milliseconds.
		"""
		if not self._initialized:
			return 0
		return lib.ma_engine_get_time_in_milliseconds(self._engine)
	def play_sound(self, file_path: str, group=None) -> bool:
		"""Play a sound file directly through the engine.
		Args:
			file_path: Path to the audio file to play.
			group: Optional sound group to attach the sound to.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		file_path_bytes = file_path.encode('utf-8')
		result = lib.ma_engine_play_sound(self._engine, file_path_bytes, group if group else ffi.NULL)
		return result == lib.MA_SUCCESS
	# Listener control methods
	@property
	def listener_count(self) -> int:
		"""Get the number of listeners in the engine.
		Returns:
			Number of listeners.
		"""
		if not self._initialized:
			return 0
		return lib.ma_engine_get_listener_count(self._engine)
	def find_closest_listener(self, x: float, y: float, z: float) -> int:
		"""Find the closest listener to a given position.
		Args:
			x: X coordinate.
			y: Y coordinate.
			z: Z coordinate.
		Returns:
			Index of the closest listener.
		"""
		if not self._initialized:
			return 0
		return lib.ma_engine_find_closest_listener(self._engine, x, y, z)
	def set_listener_position(self, listener_index: int, x: float, y: float, z: float) -> bool:
		"""Set the position of a listener.
		Args:
			listener_index: Index of the listener to modify.
			x: X coordinate.
			y: Y coordinate.
			z: Z coordinate.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		lib.ma_engine_listener_set_position(self._engine, listener_index, x, y, z)
		return True
	def get_listener_position(self, listener_index: int) -> tuple[float, float, float]:
		"""Get the position of a listener.
		Args:
			listener_index: Index of the listener.
		Returns:
			Tuple of (x, y, z) coordinates.
		"""
		if not self._initialized:
			return (0.0, 0.0, 0.0)
		pos = lib.ma_engine_listener_get_position(self._engine, listener_index)
		return (pos.x, pos.y, pos.z)
	def set_listener_direction(self, listener_index: int, x: float, y: float, z: float) -> bool:
		"""Set the direction a listener is facing.
		Args:
			listener_index: Index of the listener to modify.
			x: X component of the direction vector.
			y: Y component of the direction vector.
			z: Z component of the direction vector.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		lib.ma_engine_listener_set_direction(self._engine, listener_index, x, y, z)
		return True
	def get_listener_direction(self, listener_index: int) -> tuple[float, float, float]:
		"""Get the direction a listener is facing.
		Args:
			listener_index: Index of the listener.
		Returns:
			Tuple of (x, y, z) direction components.
		"""
		if not self._initialized:
			return (0.0, 0.0, 0.0)
		dir_vec = lib.ma_engine_listener_get_direction(self._engine, listener_index)
		return (dir_vec.x, dir_vec.y, dir_vec.z)
	def set_listener_velocity(self, listener_index: int, x: float, y: float, z: float) -> bool:
		"""Set the velocity of a listener for Doppler effect.
		Args:
			listener_index: Index of the listener to modify.
			x: X component of the velocity vector.
			y: Y component of the velocity vector.
			z: Z component of the velocity vector.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		lib.ma_engine_listener_set_velocity(self._engine, listener_index, x, y, z)
		return True
	def get_listener_velocity(self, listener_index: int) -> tuple[float, float, float]:
		"""Get the velocity of a listener.
		Args:
			listener_index: Index of the listener.
		Returns:
			Tuple of (x, y, z) velocity components.
		"""
		if not self._initialized:
			return (0.0, 0.0, 0.0)
		vel_vec = lib.ma_engine_listener_get_velocity(self._engine, listener_index)
		return (vel_vec.x, vel_vec.y, vel_vec.z)
	def set_listener_cone(self, listener_index: int, inner_angle: float, outer_angle: float, outer_gain: float) -> bool:
		"""Set the cone parameters for a listener.
		Args:
			listener_index: Index of the listener to modify.
			inner_angle: Inner cone angle in radians.
			outer_angle: Outer cone angle in radians.
			outer_gain: Gain multiplier outside the outer cone (0.0 to 1.0).
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		lib.ma_engine_listener_set_cone(self._engine, listener_index, inner_angle, outer_angle, outer_gain)
		return True
	def get_listener_cone(self, listener_index: int) -> tuple[float, float, float]:
		"""Get the cone parameters for a listener.
		Args:
			listener_index: Index of the listener.
		Returns:
			Tuple of (inner_angle, outer_angle, outer_gain).
		"""
		if not self._initialized:
			return (0.0, 0.0, 1.0)
		inner_ptr = ffi.new("float*")
		outer_ptr = ffi.new("float*")
		gain_ptr = ffi.new("float*")
		lib.ma_engine_listener_get_cone(self._engine, listener_index, inner_ptr, outer_ptr, gain_ptr)
		return (inner_ptr[0], outer_ptr[0], gain_ptr[0])
	def set_listener_world_up(self, listener_index: int, x: float, y: float, z: float) -> bool:
		"""Set the world up vector for a listener.
		Args:
			listener_index: Index of the listener to modify.
			x: X component of the up vector.
			y: Y component of the up vector.
			z: Z component of the up vector.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		lib.ma_engine_listener_set_world_up(self._engine, listener_index, x, y, z)
		return True
	def get_listener_world_up(self, listener_index: int) -> tuple[float, float, float]:
		"""Get the world up vector for a listener.
		Args:
			listener_index: Index of the listener.
		Returns:
			Tuple of (x, y, z) up vector components.
		"""
		if not self._initialized:
			return (0.0, 1.0, 0.0)  # Default up vector
		up_vec = lib.ma_engine_listener_get_world_up(self._engine, listener_index)
		return (up_vec.x, up_vec.y, up_vec.z)
	def set_listener_enabled(self, listener_index: int, enabled: bool) -> bool:
		"""Enable or disable a listener.
		Args:
			listener_index: Index of the listener to modify.
			enabled: True to enable, False to disable.
		Returns:
			True if successful, False otherwise.
		"""
		if not self._initialized:
			return False
		lib.ma_engine_listener_set_enabled(self._engine, listener_index, lib.MA_TRUE if enabled else lib.MA_FALSE)
		return True
	def is_listener_enabled(self, listener_index: int) -> bool:
		"""Check if a listener is enabled.
		Args:
			listener_index: Index of the listener.
		Returns:
			True if enabled, False if disabled.
		"""
		if not self._initialized:
			return False
		return lib.ma_engine_listener_is_enabled(self._engine, listener_index) == lib.MA_TRUE


class Sound:
	"""Represents a single audio sound that can be played, paused, and manipulated.
	The Sound class provides a high-level interface for individual audio files,
	supporting loading from files, URLs, or memory buffers. It offers comprehensive
	control over playback, volume, positioning, and 3D audio effects.
	Args:
		engine: Audio engine instance. If None, uses the global engine.
		source: Optional audio source to load immediately. Can be a file path,
			URL, or bytes object.
	Attributes:
		engine: Reference to the audio engine managing this sound.
		source: The original source used to load this sound.
		_sound: FFI pointer to the underlying miniaudio sound object.
		_loaded: Whether the sound has been successfully loaded.
	"""

	def __init__(self, engine: Engine = None, source: Optional[bytes|str] = None):
		if not engine:
			engine = _global_engine
		self.engine = engine
		self.source = source
		self._sound = None
		self._loaded = False
		if source is not None:
			self.load(source)

	def __del__(self):
		"""Cleanup the sound when the object is destroyed."""
		if hasattr(self, '_loaded') and self._loaded and self._sound:
			lib.ma_sound_uninit(self._sound)

	def load(self, source: Optional[bytes|str] = None, stream: bool = True) -> bool:
		"""Load audio from various sources.
		Args:
			source: Audio source to load. Can be:
				- String: File path or URL
				- bytes: Raw audio data
				- None: Use the source specified in constructor
			stream: Whether to stream the audio (True) or load entirely into memory (False).
		Returns:
			True if successful, False otherwise.
		"""
		if source is None:
			source = self.source
		if source is None:
			return False
		if isinstance(source, str):  # either file or URL
			if is_uri(source):
				return self.load_from_url(source, stream=stream)
			else:
				return self.load_from_file(source, stream=stream)
		else:
			return self.load_from_memory(source, stream=stream)

	def load_from_url(self, url: str, stream: bool = True) -> bool:
		"""Load audio from a URL.
		Args:
			url: URL to load audio from.
			stream: Whether to stream the audio (True) or load entirely into memory (False).
		Returns:
			True if successful, False otherwise.
		Note:
			Not yet implemented.
		"""
		# TODO: Implement URL loading with proper HTTP/FTP(s) handling
		raise NotImplementedError("URL loading not yet implemented")

	def load_from_file(self, filename: str, stream: bool = True) -> bool:
		"""Load audio from a file.
		Args:
			filename: Path to the audio file to load.
			stream: Whether to stream the audio (True) or decode entirely into memory (False).
		Returns:
			True if successful, False otherwise.
		"""
		if not self.engine._initialized:
			return False
		self._sound = ffi.new("ma_sound*")
		flags = lib.MA_SOUND_FLAG_STREAM if stream else lib.MA_SOUND_FLAG_DECODE
		filename_bytes = filename.encode('utf-8')
		result = lib.ma_sound_init_from_file(
			self.engine._engine,
			filename_bytes,
			flags,
			ffi.NULL,  # No sound group
			ffi.NULL,  # No fence
			self._sound
		)
		if result != lib.MA_SUCCESS:
			raise MiniAudioError(f"Failed to load sound from file: {result}")
		self._loaded = True
		return True

	def load_from_memory(self, data: bytes, stream: bool = True) -> bool:
		"""Load audio from memory buffer.
		Args:
			data: Raw audio data as bytes.
			stream: Whether to stream the audio (True) or decode entirely into memory (False).
		Returns:
			True if successful, False otherwise.
		Note:
			Not yet implemented.
		"""
		# TODO: Implement memory loading via a MA data source
		raise NotImplementedError("Memory loading not yet implemented")

	def play(self) -> bool:
		"""Start playing the loaded sound.
		Returns:
			True if successful, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		result = lib.ma_sound_start(self._sound)
		return result == lib.MA_SUCCESS

	def pause(self) -> bool:
		"""Pause the sound playback.
		Returns:
			True if successful, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		result = lib.ma_sound_stop(self._sound)
		return result == lib.MA_SUCCESS

	@property
	def volume(self) -> float:
		"""Get the volume of this sound.
		Returns:
			Volume level as a float (0.0 to 1.0+).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 0.0
		return lib.ma_sound_get_volume(self._sound)

	@volume.setter
	def volume(self, value: float):
		"""Set the volume of this sound.
		Args:
			value: Volume level as a float (0.0 to 1.0+).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_volume(self._sound, value)

	def stop(self) -> bool:
		"""Stop the sound playback completely.
		Returns:
			True if successful, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		result = lib.ma_sound_stop(self._sound)
		return result == lib.MA_SUCCESS

	@property
	def is_playing(self) -> bool:
		"""Check if the sound is currently playing.
		Returns:
			True if playing, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		return lib.ma_sound_is_playing(self._sound) == lib.MA_TRUE

	@property
	def looping(self) -> bool:
		"""Check if the sound is set to loop.
		Returns:
			True if looping, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		return lib.ma_sound_is_looping(self._sound) == lib.MA_TRUE

	@looping.setter
	def looping(self, value: bool):
		"""Set whether the sound should loop.
		Args:
			value: True to enable looping, False to disable.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_looping(self._sound, lib.MA_TRUE if value else lib.MA_FALSE)

	@property
	def length_in_seconds(self) -> float:
		"""Get the length of the sound in seconds.
		Returns:
			Length in seconds, or 0.0 if not loaded or unknown.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 0.0
		length_ptr = ffi.new("float*")
		result = lib.ma_sound_get_length_in_seconds(self._sound, length_ptr)
		if result == lib.MA_SUCCESS:
			return length_ptr[0]
		return 0.0

	@property
	def position_in_seconds(self) -> float:
		"""Get the current playback position in seconds.
		Returns:
			Current position in seconds, or 0.0 if not loaded.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 0.0
		cursor_ptr = ffi.new("float*")
		result = lib.ma_sound_get_cursor_in_seconds(self._sound, cursor_ptr)
		if result == lib.MA_SUCCESS:
			return cursor_ptr[0]
		return 0.0

	@position_in_seconds.setter
	def position_in_seconds(self, value: float):
		"""Seek to a specific position in the sound.
		Args:
			value: Position in seconds to seek to.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_seek_to_second(self._sound, value)


	@property
	def pitch(self) -> float:
		"""Get the current pitch of the sound.
		Returns:
			Pitch multiplier (1.0 = normal).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1.0
		return lib.ma_sound_get_pitch(self._sound)

	@pitch.setter
	def pitch(self, value: float):
		"""Set the pitch of the sound.
		Args:
			value: Pitch multiplier (1.0 = normal, 2.0 = double speed/pitch, 0.5 = half speed/pitch).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_pitch(self._sound, value)

	@property
	def pan(self) -> float:
		"""Get the current stereo pan of the sound.
		Returns:
			Pan value (-1.0 = full left, 0.0 = center, 1.0 = full right).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 0.0
		return lib.ma_sound_get_pan(self._sound)

	@pan.setter
	def pan(self, value: float):
		"""Set the stereo pan of the sound.
		Args:
			value: Pan value (-1.0 = full left, 0.0 = center, 1.0 = full right).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_pan(self._sound, value)

	@property
	def position(self) -> tuple[float, float, float]:
		"""Get the 3D position of the sound.
		Returns:
			Tuple of (x, y, z) coordinates.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return (0.0, 0.0, 0.0)
		pos = lib.ma_sound_get_position(self._sound)
		return (pos.x, pos.y, pos.z)

	@position.setter
	def position(self, value: tuple[float, float, float]):
		"""Set the 3D position of the sound.
		Args:
			value: Tuple of (x, y, z) coordinates.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		x, y, z = value
		lib.ma_sound_set_position(self._sound, x, y, z)

	def fade_in(self, duration_ms: int, start_volume: float = 0.0, end_volume: float = 1.0) -> bool:
		"""Fade in the sound over a specified duration.
		Args:
			duration_ms: Duration of the fade in milliseconds.
			start_volume: Starting volume (default: 0.0).
			end_volume: Ending volume (default: 1.0).
		Returns:
			True if successful, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		lib.ma_sound_set_fade_in_milliseconds(self._sound, start_volume, end_volume, duration_ms)
		return True

	def fade_out(self, duration_ms: int, end_volume: float = 0.0) -> bool:
		"""Fade out the sound over a specified duration.
		Args:
			duration_ms: Duration of the fade in milliseconds.
			end_volume: Ending volume (default: 0.0).
		Returns:
			True if successful, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		current_volume = self.volume
		lib.ma_sound_set_fade_in_milliseconds(self._sound, current_volume, end_volume, duration_ms)
		return True

	# Spatialization methods
	@property
	def spatialization_enabled(self) -> bool:
		"""Check if 3D spatialization is enabled for this sound.
		Returns:
			True if spatialization is enabled, False otherwise.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return False
		return lib.ma_sound_is_spatialization_enabled(self._sound) == lib.MA_TRUE

	@spatialization_enabled.setter
	def spatialization_enabled(self, value: bool):
		"""Enable or disable 3D spatialization for this sound.
		Args:
			value: True to enable spatialization, False to disable.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_spatialization_enabled(self._sound, lib.MA_TRUE if value else lib.MA_FALSE)

	@property
	def direction(self) -> tuple[float, float, float]:
		"""Get the direction vector of the sound source.
		Returns:
			Tuple of (x, y, z) direction components.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return (0.0, 0.0, 0.0)
		dir_vec = lib.ma_sound_get_direction(self._sound)
		return (dir_vec.x, dir_vec.y, dir_vec.z)

	@direction.setter
	def direction(self, value: tuple[float, float, float]):
		"""Set the direction vector of the sound source.
		Args:
			value: Tuple of (x, y, z) direction components.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		x, y, z = value
		lib.ma_sound_set_direction(self._sound, x, y, z)

	@property
	def velocity(self) -> tuple[float, float, float]:
		"""Get the velocity vector of the sound source.
		Returns:
			Tuple of (x, y, z) velocity components.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return (0.0, 0.0, 0.0)
		vel_vec = lib.ma_sound_get_velocity(self._sound)
		return (vel_vec.x, vel_vec.y, vel_vec.z)

	@velocity.setter
	def velocity(self, value: tuple[float, float, float]):
		"""Set the velocity vector of the sound source for Doppler effect.
		Args:
			value: Tuple of (x, y, z) velocity components.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		x, y, z = value
		lib.ma_sound_set_velocity(self._sound, x, y, z)

	@property
	def attenuation_model(self) -> AttenuationModel:
		"""Get the current attenuation model.
		Returns:
			AttenuationModel enum representing the attenuation model.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return AttenuationModel.NONE
		model = lib.ma_sound_get_attenuation_model(self._sound)
		return ATTENUATION_MODEL_REVERSE_MAP.get(model, AttenuationModel.NONE)

	@attenuation_model.setter
	def attenuation_model(self, value: Union[AttenuationModel, str]):
		"""Set the attenuation model for distance-based volume falloff.
		Args:
			value: AttenuationModel enum or string. Options:
				- AttenuationModel.NONE or 'none': No attenuation
				- AttenuationModel.INVERSE or 'inverse': Inverse distance attenuation
				- AttenuationModel.LINEAR or 'linear': Linear distance attenuation
				- AttenuationModel.EXPONENTIAL or 'exponential': Exponential distance attenuation
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		if isinstance(value, str):
			value = AttenuationModel(value)
		if value in ATTENUATION_MODEL_MAP:
			lib.ma_sound_set_attenuation_model(self._sound, ATTENUATION_MODEL_MAP[value])

	@property
	def positioning(self) -> PositioningMode:
		"""Get the current positioning mode.
		Returns:
			PositioningMode enum representing the positioning mode.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return PositioningMode.ABSOLUTE
		positioning = lib.ma_sound_get_positioning(self._sound)
		return POSITIONING_MODE_REVERSE_MAP.get(positioning, PositioningMode.ABSOLUTE)

	@positioning.setter
	def positioning(self, value: Union[PositioningMode, str]):
		"""Set the positioning mode for the sound.
		Args:
			value: PositioningMode enum or string. Options:
				- PositioningMode.ABSOLUTE or 'absolute': Absolute positioning in world space
				- PositioningMode.RELATIVE or 'relative': Relative positioning to listener
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		if isinstance(value, str):
			value = PositioningMode(value)
		if value in POSITIONING_MODE_MAP:
			lib.ma_sound_set_positioning(self._sound, POSITIONING_MODE_MAP[value])

	@property
	def rolloff(self) -> float:
		"""Get the current rolloff factor.
		Returns:
			Rolloff factor.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1.0
		return lib.ma_sound_get_rolloff(self._sound)

	@rolloff.setter
	def rolloff(self, value: float):
		"""Set the rolloff factor for distance attenuation.
		Args:
			value: Rolloff factor. Higher values mean more aggressive attenuation.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_rolloff(self._sound, value)

	@property
	def min_distance(self) -> float:
		"""Get the current minimum distance.
		Returns:
			Minimum distance.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1.0
		return lib.ma_sound_get_min_distance(self._sound)

	@min_distance.setter
	def min_distance(self, value: float):
		"""Set the minimum distance for attenuation calculations.
		Args:
			value: Minimum distance below which attenuation doesn't increase.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_min_distance(self._sound, value)

	@property
	def max_distance(self) -> float:
		"""Get the current maximum distance.
		Returns:
			Maximum distance.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1000.0
		return lib.ma_sound_get_max_distance(self._sound)

	@max_distance.setter
	def max_distance(self, value: float):
		"""Set the maximum distance for attenuation calculations.
		Args:
			value: Maximum distance beyond which attenuation doesn't increase further.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_max_distance(self._sound, value)

	@property
	def min_gain(self) -> float:
		"""Get the current minimum gain.
		Returns:
			Minimum gain value.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 0.0
		return lib.ma_sound_get_min_gain(self._sound)

	@min_gain.setter
	def min_gain(self, value: float):
		"""Set the minimum gain (volume) for attenuation.
		Args:
			value: Minimum gain value (0.0 to 1.0).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_min_gain(self._sound, value)

	@property
	def max_gain(self) -> float:
		"""Get the current maximum gain.
		Returns:
			Maximum gain value.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1.0
		return lib.ma_sound_get_max_gain(self._sound)

	@max_gain.setter
	def max_gain(self, value: float):
		"""Set the maximum gain (volume) for attenuation.
		Args:
			value: Maximum gain value (0.0 to 1.0+).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_max_gain(self._sound, value)

	@property
	def cone(self) -> tuple[float, float, float]:
		"""Get the sound cone parameters.
		Returns:
			Tuple of (inner_angle, outer_angle, outer_gain).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return (0.0, 0.0, 1.0)
		inner_ptr = ffi.new("float*")
		outer_ptr = ffi.new("float*")
		gain_ptr = ffi.new("float*")
		lib.ma_sound_get_cone(self._sound, inner_ptr, outer_ptr, gain_ptr)
		return (inner_ptr[0], outer_ptr[0], gain_ptr[0])

	@cone.setter
	def cone(self, value: tuple[float, float, float]):
		"""Set the sound cone for directional audio.
		Args:
			value: Tuple of (inner_angle, outer_angle, outer_gain) where:
				- inner_angle: Inner cone angle in radians where sound is at full volume.
				- outer_angle: Outer cone angle in radians where sound starts to attenuate.
				- outer_gain: Gain multiplier outside the outer cone (0.0 to 1.0).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		inner_angle, outer_angle, outer_gain = value
		lib.ma_sound_set_cone(self._sound, inner_angle, outer_angle, outer_gain)

	@property
	def doppler_factor(self) -> float:
		"""Get the current Doppler effect factor.
		Returns:
			Doppler factor.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1.0
		return lib.ma_sound_get_doppler_factor(self._sound)

	@doppler_factor.setter
	def doppler_factor(self, value: float):
		"""Set the Doppler effect factor.
		Args:
			value: Doppler factor (1.0 = normal, 0.0 = no Doppler effect).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_doppler_factor(self._sound, value)

	@property
	def directional_attenuation_factor(self) -> float:
		"""Get the current directional attenuation factor.
		Returns:
			Directional attenuation factor.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 1.0
		return lib.ma_sound_get_directional_attenuation_factor(self._sound)

	@directional_attenuation_factor.setter
	def directional_attenuation_factor(self, value: float):
		"""Set the directional attenuation factor.
		Args:
			value: Directional attenuation factor (0.0 to 1.0).
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_directional_attenuation_factor(self._sound, value)

	@property
	def direction_to_listener(self) -> tuple[float, float, float]:
		"""Get the direction vector from this sound to the listener.
		Returns:
			Tuple of (x, y, z) direction components pointing towards the listener.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return (0.0, 0.0, 0.0)
		dir_vec = lib.ma_sound_get_direction_to_listener(self._sound)
		return (dir_vec.x, dir_vec.y, dir_vec.z)

	@property
	def pinned_listener_index(self) -> int:
		"""Get the index of the pinned listener.
		Returns:
			Listener index, or -1 if not pinned.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return -1
		return lib.ma_sound_get_pinned_listener_index(self._sound)

	@pinned_listener_index.setter
	def pinned_listener_index(self, value: int):
		"""Pin this sound to a specific listener.
		Args:
			value: Index of the listener to pin to.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return
		lib.ma_sound_set_pinned_listener_index(self._sound, value)

	@property
	def listener_index(self) -> int:
		"""Get the index of the listener this sound is currently using.
		Returns:
			Listener index.
		"""
		if not hasattr(self, '_loaded') or not self._loaded:
			return 0
		return lib.ma_sound_get_listener_index(self._sound)

def play_sound(file_path: str, group=None) -> bool:
	return _global_engine.play_sound(path, group)


_global_engine = Engine()
