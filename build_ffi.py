import os
import sys
import subprocess
from pathlib import Path
from cffi import FFI

root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
	sys.path.append(str(root_dir))

lib_dir = root_dir / "lib"


def _pkgconfig(*args):
	try:
		r = subprocess.run(["pkg-config"] + list(args), capture_output=True, text=True)
		return r.returncode == 0, r.stdout.strip()
	except FileNotFoundError:
		return False, ""


def _find_via_pkgconfig():
	pkgs = ["opus", "opusfile", "ogg", "vorbis", "vorbisfile", "libcurl"]
	ok, _ = _pkgconfig("--exists", *pkgs)
	if not ok:
		return None
	_, cflags = _pkgconfig("--cflags-only-I", *pkgs)
	_, ldflags = _pkgconfig("--libs-only-L", *pkgs)
	inc = [f[2:] for f in cflags.split() if f.startswith("-I")]
	ldirs = [f[2:] for f in ldflags.split() if f.startswith("-L")]
	return inc, ldirs


def _find_via_vcpkg():
	vcpkg_dir = root_dir / "vcpkg"
	if not vcpkg_dir.exists():
		return None
	try:
		import vcpkg as _vcpkg
	except ImportError:
		return None
	print("vcpkg found, installing packages...")
	_vcpkg.build()
	if _vcpkg.install_path.exists():
		return (
			[str(_vcpkg.install_path / "include")],
			[str(_vcpkg.install_path / "lib")],
		)
	return None


include_dirs = [str(root_dir), str(lib_dir)]
library_dirs = []

if os.environ.get("SOUNDOBJ_INCLUDE_DIRS"):
	include_dirs += os.environ["SOUNDOBJ_INCLUDE_DIRS"].split(os.pathsep)
if os.environ.get("SOUNDOBJ_LIB_DIRS"):
	library_dirs += os.environ["SOUNDOBJ_LIB_DIRS"].split(os.pathsep)
deps_found = bool(os.environ.get("SOUNDOBJ_LIB_DIRS"))
if not deps_found and sys.platform != "win32":
	result = _find_via_pkgconfig()
	if result:
		inc, ldirs = result
		include_dirs += inc
		library_dirs += ldirs
		deps_found = True
if not deps_found:
	result = _find_via_vcpkg()
	if result:
		inc, ldirs = result
		include_dirs += inc
		library_dirs += ldirs
		deps_found = True
if not deps_found:
	if sys.platform == "win32":
		raise RuntimeError(
			"Could not find native dependencies. Options:\n"
			"  1. Clone with submodules: git clone --recurse-submodules https://github.com/cartertemm/soundobj\n"
			"  2. Set SOUNDOBJ_INCLUDE_DIRS and SOUNDOBJ_LIB_DIRS to point at your opus/vorbis/curl installs\n"
		)
	else:
		raise RuntimeError(
			"Could not find native dependencies. Install them first:\n"
			"  Debian/Ubuntu:  apt install libopus-dev libopusfile-dev libvorbis-dev libogg-dev libcurl4-openssl-dev\n"
			"  macOS:          brew install opus opusfile libvorbis libogg curl\n"
			"Then retry: pip install soundobj\n"
		)

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

ffibuilder = FFI()
with open(root_dir / "declarations.h", "r") as f:
	cdefs = f.read()
ffibuilder.cdef(cdefs)

ffibuilder.set_source("_c_miniaudio", """
	#include <stdint.h>
	#include <stdlib.h>
	#define MINIAUDIO_IMPLEMENTATION
	#include <miniaudio.h>
	#include "lib/miniaudio_libopus.h"
	#include "lib/miniaudio_libvorbis.h"

	#include "lib/miniaudio_libopus.c"
	#include "lib/miniaudio_libvorbis.c"
	#include <curl/curl.h>
	#include "lib/url_vfs.c"
	#include "lib/soundobj_wasapi_monitor.c"

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
