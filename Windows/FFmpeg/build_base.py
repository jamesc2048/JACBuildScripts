import enum
import multiprocessing
import subprocess as sp
import time
from path import Path
import os

class BuilderBase:
    NUM_CORES = multiprocessing.cpu_count()

    def __init__(self, name, git_address, linkage):
        self.name = name
        self.git_address = git_address
        self.linkage = linkage

        self.git_clone_path = Path(f"{self.name}-git")
        self.build_path = Path(f"build-{self.name}-{self.linkage}-git")
        
        self.build_abspath = self.build_path.abspath()


    def update_sources(self):
        if not self.git_clone_path.exists():
            self.run(f"git clone {self.git_address} {self.git_clone_path}")
            os.chdir(self.git_clone_path)
        else:
            os.chdir(self.git_clone_path)
            self.run(f"git pull")

        self.run("git status")

        try:
            self.version = self.run("git describe --tags")
            print(self.version)
        except Exception as e:
            print("Can't get tag version")
            self.version = None

        # workaround for directory locking
        time.sleep(1)

        os.chdir("..")

    def build(self):
        pass

    @staticmethod
    def run(cmd, print_output=True):
        if print_output: print("Cmd: " + cmd)

        out = sp.check_output(cmd, shell=True).decode("utf-8")
        if print_output: print(out)
        
        # trim pesky newline
        if len(out) and out[-1] == "\n":
            out = out[:-1]

        # workaround for directory locking
        time.sleep(1)

        return out

    @staticmethod
    def run_in_msys(cmd, working_dir=None, hide_window=False):
        if isinstance(cmd, (list, tuple)):
            cmd ="; ".join(cmd)

        if not Path(r"C:\msys64\msys2_shell.cmd").exists():
            raise Exception("Need msys2 install in default path C:\\msys64\\")
        
        if working_dir:
            cmd = rf"""cd '{working_dir}'; """ + cmd

        # hide_window_opt = "-w hide" if hide_window else ""
        # TODO: use this to hide window C:\msys64\usr\bin\mintty.exe -w hide /bin/env MSYSTEM=MINGW64 /bin/bash -lc /c/path/to/your_program.exe

        return BuilderBase.run(rf"""C:\msys64\msys2_shell.cmd -mingw64 -c "set -xe; {cmd};" """)