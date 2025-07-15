# build_exe.py
# Script to convert main.py into an executable using PyInstaller

import subprocess
import sys

def build_executable():
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "python_exe_converter",
        "main.py"
    ]
    try:
        subprocess.check_call(pyinstaller_cmd)
        print("Executable built successfully: dist/python_exe_converter.exe")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")

if __name__ == "__main__":
    build_executable()