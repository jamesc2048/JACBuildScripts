import sys
import subprocess as sp
import os
from pathlib import *
import requests
from zipfile import ZipFile
import shutil
from threading import Thread
import psutil

if os.name != "nt":
    raise Exception("Only Windows supported at the moment")

def download(url, filename):
    print("Download", url, filename)

    try:
        r = requests.get(url, stream=True)
        
        done = 0

        with open(filename, "wb") as f:
            for c in r.iter_content(256 * 1024):
                f.write(c)
                done += len(c)
                print(f"Download {float(done) / 1024. / 1024.:.2f} MB", end="\r")

        print()
    except:
        raise


def main():
    if not Path("opencv-4.5.0.zip").exists():
        download("https://github.com/opencv/opencv/archive/4.5.0.zip", "opencv-4.5.0.zip")

    if not Path("opencv_contrib-4.5.0.zip").exists():
        download("https://github.com/opencv/opencv_contrib/archive/4.5.0.zip", "opencv_contrib-4.5.0.zip")

    shutil.rmtree("buildtrees", ignore_errors=True)
    
    print("Unzip")

    os.mkdir("buildtrees")
    with ZipFile("opencv-4.5.0.zip", "r") as zf:
        zf.extractall("buildtrees")

    with ZipFile("opencv_contrib-4.5.0.zip", "r") as zf:
        zf.extractall("buildtrees")

    print("Build")

    shutil.rmtree("logs", ignore_errors=True)
    os.mkdir("logs")
    logs = [ open("logs/simple-log.txt", "w"),
            open("logs/simple-static-log.txt", "w"),
            open("logs/contrib-log.txt", "w"),
            open("logs/contrib-static-log.txt", "w") ]

    os.chdir("buildtrees")

    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)

    class Runner():
        def __init__(self, exe, log):
            self.exe, self.log = exe, log

        def __call__(self):
            sp.check_call(self.exe, stdout=self.log, stderr=self.log)

    threads = [ Thread(target=Runner("..\\variants\\simple.bat", logs[0])), 
                Thread(target=Runner("..\\variants\\simple-static.bat", logs[1])),
                Thread(target=Runner("..\\variants\\contrib.bat", logs[2])), 
                Thread(target=Runner("..\\variants\\contrib-static.bat", logs[3])) ]

    [t.start() for t in threads]
    [t.join() for t in threads]

    print("Done")

    [l.close() for l in logs]
    #shutil.move("build-4.5-simple/")
    #shutil.move("build-4.5-simple-static/")

if __name__ == "__main__":
    main()