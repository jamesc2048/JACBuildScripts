"""
FFmpeg Git build script
Needs:
Msys2 setup with GCC
Git in path
"path" Python library
"""

import subprocess as sp
import os
from path import Path
import zipfile as zf
import multiprocessing
import time

original_dir = os.getcwd()

def build():
    def run(cmd, print_output=True):
        if print_output: print("Cmd: " + cmd)
        out = sp.check_output(cmd).decode("utf-8")
        if print_output: print(out)
        
        # trim pesky newline
        if len(out) and out[-1] == "\n":
            out = out[:-1]
        return out

    GIT_CLONE_DIR = "ffmpeg-git"
    BUILD_DIR = "build-ffmpeg-git"
    NUM_CORES = multiprocessing.cpu_count()

    git_clone_dir = Path(GIT_CLONE_DIR)
    build_dir = Path(BUILD_DIR)

    build_abspath = build_dir.abspath()

    if not git_clone_dir.exists():
        run(f"git clone https://github.com/FFmpeg/FFmpeg.git {GIT_CLONE_DIR}")
        os.chdir(git_clone_dir)
    else:
        os.chdir(git_clone_dir)
        run(f"git pull")

    run("git status")
    version = run("git describe --tags")

    os.chdir("..")

    if build_dir.exists():
        build_dir.rmtree()

    build_dir.mkdir()

    os.chdir(build_dir)

    '''
    Build with MSVC (uses Windows C runtime instead of GCC!)
    Launch VS 2017 x64 Native Tools Command Prompt
    C:\msys64\msys2_shell.cmd -mingw64 -use-full-path
    ./configure --target-os=win64 --arch=x86_64 --toolchain=msvc --enable-shared --prefix=install
    make -j16
    '''

    configure_options = ["--disable-lzma",
                        "--disable-sdl2",
                        "--prefix=install" ]

    # TODO command line opt
    shared_build = True
    license="lgpl2.1"

    if shared_build:
        build_type = "shared"
        configure_options.append("--enable-shared")
    else:
        build_type = "static"
        configure_options.append("--disable-shared")

    build_name = f"ffmpeg-{build_type}-{version}-{license}"
    configure_options.append(f"--extra-version={build_name}")

    build_script = (
        f"../{git_clone_dir}/configure " + " ".join(configure_options) + " | tee configureLog.txt",
        f"make -j{NUM_CORES}" + " | tee makeLog.txt", 
        "make install" + " | tee installLog.txt", 
        "cp *Log.txt install",
        f"mv install {build_name}",
        f"zip -r {build_name}.zip {build_name}",
        f"mv {build_name}.zip ..",
    )

    def run_in_msys(cmd, working_dir=None, hide_window=True):
        # -w hide to hide window
        if working_dir:
            cmd = rf"""cd '{working_dir}'; """ + cmd

        return run(rf"""C:\msys64\msys2_shell.cmd -mingw64 -c "set -xe; {cmd}" """)

    for bs in build_script:
        run_in_msys(bs, working_dir=build_abspath)

    os.chdir(original_dir)

while True: 
    build()
    # test run every hour
    time.sleep(60 * 60)
