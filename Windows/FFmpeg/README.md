FFmpeg build scripts

Run "build_all.py" to run all the libraries.
Currently only working on Windows x64 static.

Libraries:
- libx264 git
- libx265 git
- libsvt-av1 git
- libSDL2 git

You're expected to run this in a VM as the script installs the libs inside the MSYS environment.

Requires:
- Python 3.6+
- MSYS2 install in default location C:\msys64
- MSYS installs: 
-- pacman -Syu && pacman -S base-devel mingw-w64-x86_64-toolchain

Plans:
- [ ] More libs
- [ ] Daily build server
- [ ] Linux build
- [ ] Local MSYS so it doesn't install into global MSYS
