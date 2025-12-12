from pathlib import Path
import shutil
import subprocess
import sys

vcpkg_path = Path(__file__, "..", "vcpkg", "vcpkg" if sys.platform != "win32" else "vcpkg.exe").resolve()
# Try to determine triplet being built for, logic probably could be improved
if sys.platform == "win32": triplet = "x64-windows-static-md"
elif sys.platform == "darwin": triplet = "arm64-osx-static"
elif sys.platform == "linux": triplet = "x64-linux-static"
else: sys.exit("unable to determine vcpkg triplet.")
install_path = Path(__file__, "..", "vcpkg_installed", triplet).resolve()

def bootstrap_vcpkg():
	if vcpkg_path.exists() and vcpkg_path.is_file():
		return
	print("Bootstrapping VCPKG...")
	if sys.platform == "win32":
		subprocess.check_output(vcpkg_path.parent / "bootstrap-vcpkg.bat")
	else:
		subprocess.check_output(vcpkg_path.parent / "bootstrap-vcpkg.sh")

def build():
	bootstrap_vcpkg()
	print("Performing VCPKG install...")
	try:
		subprocess.check_output([vcpkg_path, "install", "--triplet", triplet])
	except subprocess.CalledProcessError as cpe:
		sys.exit(f"Building packages for {triplet} failed with error code {cpe.returncode}.\n{cpe.output.decode()}")

if __name__ == "__main__":
	build()
