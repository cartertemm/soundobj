import os
import sys
from pathlib import Path
from cffi import FFI
import vcpkg
lib_dir = Path(os.getcwd()) / "lib"
if not vcpkg.install_path.exists():
	vcpkg.build()
ffibuilder = FFI()


with open("declarations.h", "r") as f:
	cdefs = f.read()
ffibuilder.cdef(cdefs)

ffibuilder.set_source("_c_miniaudio", """
	#include <stdint.h>
	#include <stdlib.h>
	#define MINIAUDIO_IMPLEMENTATION
	#include "lib/miniaudio.h"
	#include "lib/miniaudio_libopus.h"
	#include "lib/miniaudio_libvorbis.h"
	ma_decoding_backend_vtable** soundobj_get_custom_decoders(ma_uint32* count) {
		static ma_decoding_backend_vtable* custom_decoders[2]; // Can't use quick initialization in c because of nonconstance.
		custom_decoders[0] = ma_decoding_backend_libvorbis;
		custom_decoders[1] = ma_decoding_backend_libopus;
		if (count) *count = sizeof(custom_decoders) / sizeof(custom_decoders[0]);
		return custom_decoders;
	}
""",
	sources = ["lib/miniaudio_libopus.c", "lib/miniaudio_libvorbis.c"],
	include_dirs=[lib_dir, str(vcpkg.install_path / "include")],
	library_dirs=[str(vcpkg.install_path / "lib")],
	libraries=["opus", "opusfile", "ogg", "vorbis", "vorbisfile"]
)

ffibuilder.compile(verbose=True)
