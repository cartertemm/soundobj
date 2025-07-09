# SoundObj

A modern Python wrapper for the [miniaudio](https://miniaud.io/) library, providing high-level audio playback and 3D spatialization capabilities.

## Another audio library? Why?

It's a reasonable question.

The short version is that I couldn't find one that did what I wanted.

As of mid-2025, you either get a specialized set of features (playsound), a bloated installation that does way more than sound (pyglet/pygame/etc), licensing restrictions (bass/sound_lib), EOL/lack of support (Libaudioverse/Synthizer), data sciency stuff, or low-level interfaces (PyAudio/PyMiniaudio).

To be clear, I'm not knocking any of these libraries. I have used all of them once or twice, and have code in both pybass and sound_lib.
At the time of writing, they are admitedly far more battle tested. In fact, I am likely to use them again and encourage you to do the same if they better serve your use case.

That said, I wanted something portable, permissive, and that just works with an API that is familiar or that someone could pick up and immediately start hacking on.

## Features

- Truly simple audio playback
- Support for WAV, MP3, FLAC, AIFF, AU, OGG Vorbis, and everything miniaudio is able to work with
- Adjust volume, pitch, pan, and spatial properties during playback
- Full support for positional audio, distance attenuation, and Doppler effects
- Clean property-based Python interface
- Support for multiple 3D audio listeners
- Customizable engine settings for different use cases
- Easy to extend, assuming you know a little bit of C and feel comfortable adding FFI declarations

## Installation

### Prerequisites

- Python 3.11+ (probably works on lower versions as well, this just hasn't been tested)
- cffi library
- miniaudio library (included in `lib/` directory)

### Build Instructions

1. Clone the repository:
```bash
git clone https://github.com/cartertemm/soundobj.git
cd soundobj
```

2. Install Python dependencies:
```bash
pip install cffi
```

3. Build the FFI wrapper:
```bash
python build_ffi.py
```

## Roadmap

- [ ] Upload to PyPI
- [ ] Memory and URL streams
- [ ] A more comprehensive environment for managing multiple sounds simultaniously
- [ ] More demos/examples
- [ ] Optional support for HRTF, now that [Steam Audio](https://github.com/ValveSoftware/steam-audio) has been made open-source and is licensed under Apache-2.0. This wouldn't be included by default but would be an optional dependency for those who need it.

### How you can help

Test, test, test. If you get weird behavior, open an issue and tell me about it.
If you are willing and able, hack on one of these features.

## Quick Start

Most things should be pretty self explanatory, as this library is a high-level API over the already high-level ma_engine API.
If not, the [Miniaudio programming manual](https://miniaud.io/docs/manual/index.html) is a good starting point. It explains concepts like the coordinate system, positioning in 3D space, attenuation, etc.

### Basic Audio Playback

```python
import soundobj

# Create a sound object and load an audio file
snd = soundobj.Sound("path/to/audio.wav")
snd.play()  # Play the sound
snd.looping = True  # Enable looping
snd.volume = 0.8
snd.pitch = 1.2
# Wait a bit
snd.stop()
```

### 3D Spatial Audio

```python
import soundobj
from soundobj import AttenuationModel, PositioningMode

# Create an engine with custom configuration
config = soundobj.EngineConfig(
    channels=2,
    sampleRate=44100,
    listenerCount=1
)
engine = soundobj.Engine(config)
# Create a 3D positioned sound and enable spacialization
sound = soundobj.Sound(engine, "footsteps.wav")
sound.spatialization_enabled = True

# Position the sound in 3D space
sound.position = (5.0, 0.0, 10.0)  # (x, y, z)
sound.direction = (0.0, 0.0, -1.0)  # facing negative Z
# Configure distance attenuation
sound.attenuation_model = AttenuationModel.INVERSE
sound.min_distance = 1.0
sound.max_distance = 100.0
sound.rolloff = 2.0

# Set up velocity for Doppler effect
sound.velocity = (-2.0, 0.0, 0.0)  # moving left

# Configure sound cone for directional audio
sound.cone = (0.5, 1.0, 0.3)  # (inner_angle, outer_angle, outer_gain)
sound.play()
```

### Engine and Listener Management

```python
import soundobj

engine = soundobj.Engine()

# Get engine information
print(f"Channels: {engine.channels}")
print(f"Sample Rate: {engine.sample_rate}")
print(f"Listeners: {engine.listener_count}")

# Configure listener position and orientation
engine.set_listener_position(0, 0.0, 0.0, 0.0)  # listener at origin
engine.set_listener_direction(0, 0.0, 0.0, 1.0)  # facing positive Z
engine.set_listener_velocity(0, 1.0, 0.0, 0.0)   # moving right

# Set world up vector (for 3D orientation)
engine.set_listener_world_up(0, 0.0, 1.0, 0.0)   # Y is up

# Enable/disable listeners
engine.set_listener_enabled(0, True)
```

## API Reference

### Classes

#### Engine

The main audio engine that manages playback and 3D audio processing globally. First start with an instance of `Sound` and fall back to this if needed.

**Properties:**
- `volume`: Master volume (0.0 to 1.0+)
- `channels`: Number of output channels (read-only)
- `sample_rate`: Audio sample rate in Hz (read-only)
- `time_in_milliseconds`: Current engine time (read-only)
- `listener_count`: Number of 3D listeners (read-only)

**Methods:**
- `start()`: Start the audio engine
- `stop()`: Stop the audio engine
- `play_sound(file_path, group=None)`: Play a sound file directly
- `find_closest_listener(x, y, z)`: Find nearest listener to position
- `set_listener_position(index, x, y, z)`: Set listener position
- `get_listener_position(index)`: Get listener position
- `set_listener_direction(index, x, y, z)`: Set listener orientation
- `get_listener_direction(index)`: Get listener orientation

#### Sound

Represents an individual audio sound with full control over playback and 3D properties.

**Basic Properties:**
- `volume`: Sound volume (0.0 to 1.0+)
- `pitch`: Playback speed/pitch multiplier (1.0 = normal)
- `pan`: Stereo pan (-1.0 = left, 0.0 = center, 1.0 = right)
- `looping`: Enable/disable looping playback
- `is_playing`: Check if currently playing (read-only)
- `length_in_seconds`: Audio duration (read-only)
- `position_in_seconds`: Current playback position (get/set)

**3D Spatial Properties:**
- `position`: 3D position as (x, y, z) tuple
- `direction`: Direction vector as (x, y, z) tuple
- `velocity`: Velocity vector for Doppler effect
- `spatialization_enabled`: Enable/disable 3D audio processing
- `attenuation_model`: Distance attenuation model (enum or string)
- `positioning`: Positioning mode (enum or string)

**Distance and Attenuation:**
- `rolloff`: Distance attenuation rolloff factor
- `min_distance`: Minimum distance for attenuation
- `max_distance`: Maximum distance for attenuation
- `min_gain`: Minimum volume level
- `max_gain`: Maximum volume level

**Advanced 3D Properties:**
- `cone`: Directional audio cone as (inner_angle, outer_angle, outer_gain)
- `doppler_factor`: Doppler effect intensity (1.0 = normal)
- `directional_attenuation_factor`: Directional volume reduction
- `direction_to_listener`: Vector pointing to listener (read-only)
- `pinned_listener_index`: Pin sound to specific listener
- `listener_index`: Current listener index (read-only)

**Methods:**
- `load(source, stream=True)`: Load audio from file, URL, or bytes
- `load_from_file(filename, stream=True)`: Load from file
- `load_from_url(url, stream=True)`: Load from URL (not implemented)
- `load_from_memory(data, stream=True)`: Load from memory (not implemented)
- `play()`: Start playback
- `pause()`: Pause playback
- `stop()`: Stop playback
- `fade_in(duration_ms, start_vol=0.0, end_vol=1.0)`: Fade in effect
- `fade_out(duration_ms, end_vol=0.0)`: Fade out effect

#### EngineConfig

Configuration options for engine initialization.

**Attributes:**
- `listenerCount`: Number of 3D listeners (default: 0 = auto)
- `channels`: Output channels (default: 0 = auto)
- `sampleRate`: Sample rate in Hz (default: 0 = auto)
- `periodSizeInFrames`: Period size in frames (default: 0 = auto)
- `periodSizeInMilliseconds`: Period size in ms (default: 0 = auto)
- `noAutoStart`: Don't auto-start engine (default: False)
- `noDevice`: Initialize without audio device (default: False)

### Enums

#### AttenuationModel

Distance-based volume attenuation models:
- `NONE`: No distance attenuation
- `INVERSE`: Realistic inverse distance attenuation
- `LINEAR`: Linear distance attenuation
- `EXPONENTIAL`: Exponential distance attenuation

#### PositioningMode

Sound positioning modes:
- `ABSOLUTE`: Position in world coordinates
- `RELATIVE`: Position relative to listener

### Exceptions

#### MiniAudioError

Raised when miniaudio operations fail (engine initialization, file loading, etc.).

## Licensing

This module is both released under the MIT and into the public domain. Choose which ever you prefer.

### MIT

Copyright (c) 2025 Carter Temm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Public Domain

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgments

- [miniaudio](https://miniaud.io/) by David Reid - The excellent underlying audio library
- [CFFI](https://cffi.readthedocs.io/) - For the Python/C integration. If I had to use ctypes I probably wouldn't have bothered.
