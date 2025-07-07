import os
from pathlib import Path
from cffi import FFI


lib_dir = Path(os.getcwd()) / "lib"
ffibuilder = FFI()


with open("declarations.h", "r") as f:
	cdefs = f.read()
ffibuilder.cdef(cdefs)

ffibuilder.set_source("_c_miniaudio", """
	#include <stdint.h>
	#include <stdlib.h>
	#define MINIAUDIO_IMPLEMENTATION
	#include "lib/miniaudio.h"
""",
	include_dirs=[lib_dir]
)

ffibuilder.compile(verbose=True)
