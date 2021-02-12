import enum
import multiprocessing
import subprocess as sp
import time
from path import Path
import os
import requests
import zipfile
import os

class BuilderBase:
    NUM_CORES = multiprocessing.cpu_count()

    def __init__(self, name, git_address, linkage):
        self.name = name
        self.git_address = git_address
        self.linkage = linkage

        self.base_path = Path(__file__).dirname()

        self.git_clone_path = Path(f"{self.name}-git")
        self.build_path = Path(f"build-{self.name}-{self.linkage}-git")
        
        self.build_abspath = self.build_path.abspath()
        self.git_path = self.base_path / "tools/git"
        self.git_exe_path = (self.git_path / "bin/git.exe").abspath()

        self.msys_path = self.base_path / Path("tools/msys64")

    def fetch_git(self):
        if not self.git_exe_path.exists():
            print("Fetching PortableGit archive")

            try:
                self.git_path.makedirs_p()
                # TODO put on github files?
                r = requests.get("https://crisafulli.me/public/JACBuildScripts/git_portable_2.30.1.zip", stream=True)
                
                git_zip_path = self.git_path / "git_portable_2.30.1.zip"
                total = 0

                with open(git_zip_path, "wb") as f:
                    for c in r.iter_content(chunk_size=64 * 1024):
                        print(f"Downloaded {total / 1024. / 1024.:.2f} MB / {int(r.headers['Content-Length']) / 1024. / 1024.:.2f} MB", end="\r")
                        f.write(c)
                        total += len(c)

                print()

                with zipfile.ZipFile(git_zip_path) as zf:
                    print("Extracting Git")
                    zf.extractall(self.git_path)
                
                os.remove(git_zip_path)

            except Exception as e:
                print(str(e))
                raise


    def fetch_msys(self):
        if not self.msys_path.exists():
            print("Fetching MSYS64 archive")

            try:
                self.msys_path.makedirs_p()
                # TODO put on github files?
                r = requests.get("https://crisafulli.me/public/JACBuildScripts/msys64.zip", stream=True)
                
                msys_zip_path = self.msys_path / "msys64.zip"
                total = 0

                with open(msys_zip_path, "wb") as f:
                    for c in r.iter_content(chunk_size=64 * 1024):
                        print(f"Downloaded {total / 1024. / 1024.:.2f} MB / {int(r.headers['Content-Length']) / 1024. / 1024.:.2f} MB", end="\r")
                        f.write(c)
                        total += len(c)

                print()

                with zipfile.ZipFile(msys_zip_path) as zf:
                    print("Extracting MSYS64")
                    zf.extractall(self.msys_path)
                
                os.remove(msys_zip_path)

            except Exception as e:
                print(str(e))
                raise
                
        #print("Updating MSYS")
        #self.run_in_msys("pacman -Sy --noconfirm", fetch_msys=False)
        print("Installing compiler")
        self.run_in_msys("pacman -S --noconfirm --needed base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake mingw-w64-x86_64-nasm mingw-w64-x86_64-yasm", fetch_msys=False)

    def update_sources(self):
        self.fetch_git()

        if not self.git_clone_path.exists():
            self.run(f"{self.git_exe_path} clone {self.git_address} {self.git_clone_path}")
            os.chdir(self.git_clone_path)
        else:
            os.chdir(self.git_clone_path)
            # TODO!?
            #self.run(f"{self.git_exe_path} pull --ff-only")

        self.run(f"{self.git_exe_path} status")

        try:
            self.version = self.run(f"{self.git_exe_path} describe --tags")
            print(self.version)
        except Exception as e:
            print("Can't get tag version")
            self.version = None

        os.chdir("..")

    def build(self):
        pass

    def run(self, cmd, print_output=True):
        if print_output: print("Cmd: " + cmd)

        out = sp.check_output(cmd, shell=True).decode("utf-8")
        if print_output: print(out)
        
        # trim pesky newline
        if len(out) and out[-1] == "\n":
            out = out[:-1]

        # workaround for directory locking
        time.sleep(1)

        return out

    def run_in_msys(self, cmd, working_dir=None, hide_window=False, fetch_msys=True):
        if fetch_msys:
            self.fetch_msys()

        if isinstance(cmd, (list, tuple)):
            cmd ="; ".join(cmd)

        if not (self.msys_path / "msys2_shell.cmd").exists():
            raise Exception("Need msys2 install in default path C:\\msys64\\")
        
        if working_dir:
            cmd = rf"""cd '{working_dir}'; """ + cmd

        # hide_window_opt = "-w hide" if hide_window else ""
        # TODO: use this to hide window C:\msys64\usr\bin\mintty.exe -w hide /bin/env MSYSTEM=MINGW64 /bin/bash -lc /c/path/to/your_program.exe

        return self.run(rf"""{self.msys_path}\msys2_shell.cmd -mingw64 -c "set -xe; {cmd};" """)