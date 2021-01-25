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

        out = sp.check_output(cmd, shell=True).decode("utf-8")
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
    script_dir_abspath = Path(__file__).dirname().abspath()

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

    configure_options = [
                        "--disable-autodetect",
                        "--enable-nonfree",
                        "--enable-gpl",
                        "--enable-version3",
                        "--enable-w32threads",
                        "--extra-libs=/mingw64/x86_64-w64-mingw32/lib/libwinpthread.a",
                        "--prefix=install",
                        #"--enable-libx264",
                        ]

    # TODO command line opt
    shared_build = False
    license = "gpl3"

    if shared_build:
        build_type = "shared"
        configure_options.append("--enable-shared")
        configure_options.append("--disable-static")
    else:
        build_type = "static"
        configure_options.append("--disable-shared")
        configure_options.append("--enable-static")

    build_name = f"{build_type}-{version}"
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

    def run_in_msys(cmd, working_dir=None, hide_window=False):
        if working_dir:
            cmd = rf"""cd '{working_dir}'; """ + cmd

        # hide_window_opt = "-w hide" if hide_window else ""
        # TODO: use this to hide window C:\msys64\usr\bin\mintty.exe -w hide /bin/env MSYSTEM=MINGW64 /bin/bash -lc /c/path/to/your_program.exe

        return run(rf"""C:\msys64\msys2_shell.cmd -mingw64 -c "set -xe; {cmd};" """)

    script = "; ".join(build_script)
    print(script)

    run_in_msys(script, working_dir=build_abspath, hide_window=True)

    os.chdir(original_dir)

while True: 
    build()
    # test run every hour
    time.sleep(60 * 60)
