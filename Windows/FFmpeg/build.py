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

    configure_options = [
                        "--target-os=win64",
                        "--arch=x86_64", 
                        "--toolchain=msvc",
                        "--disable-zlib",
                        "--disable-iconv",
                        "--enable-nonfree",
                        "--enable-gpl",
                        "--enable-version3",
                        "--prefix=install" ]

    # TODO command line opt
    shared_build = False
    license = "gpl3"

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
        "make" + " | tee makeLog.txt", 
        "make install" + " | tee installLog.txt", 
        "cp *Log.txt install",
        f"mv install {build_name}",
        f"zip -r {build_name}.zip {build_name}",
        f"mv {build_name}.zip ..",
    )

    def run_in_msys(cmd, tools, working_dir=None, hide_window=False):
        if working_dir:
            cmd = rf"""cd '{working_dir}'; """ + cmd

        # hide_window_opt = "-w hide" if hide_window else ""
        # TODO: use this to hide window C:\msys64\usr\bin\mintty.exe -w hide /bin/env MSYSTEM=MINGW64 /bin/bash -lc /c/path/to/your_program.exe

        mingw_opt = "-mingw64" if tools == "mingw" else ""
        vs_tools_opt = r""""C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 && """ if tools == "vs2019" else ""
        vs_path_opt = "-use-full-path" if len(vs_tools_opt) > 0 else ""

        return run(rf"""{vs_tools_opt} C:\msys64\msys2_shell.cmd {vs_path_opt} {mingw_opt} -c "set -xe; {cmd};" """)

    run_in_msys("; ".join(build_script), tools="vs2019", working_dir=build_abspath, hide_window=True)

    os.chdir(original_dir)

while True: 
    build()
    # test run every hour
    time.sleep(60 * 60)
