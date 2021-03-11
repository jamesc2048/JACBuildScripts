"""
FFmpeg Git build script
Needs:
Msys2 setup with GCC
Git in path
"path" Python library
"""

from buildX264 import X264Builder
from buildX265 import X265Builder
from buildSVTAV1 import SVTAV1Builder
from buildFFmpeg import FFmpegBuilder
from buildSDL2 import SDL2Builder

from path import Path
import zipfile as zf
import os

base_dir = Path(__file__).dirname()
version_file = "versions.txt"

for build_dir in (d for d in base_dir.dirs() if d.basename().startswith("build-")):
    print("Delete build dir", build_dir)
    build_dir.rmtree()

Path(version_file).remove_p()

deps = [
        X264Builder(),
        X265Builder(),
        SVTAV1Builder(),
        SDL2Builder(),
    ]

for dep in deps:
    print("Building dep", dep.name)
    
    dep.build()
    base_dir.chdir()

    with open(version_file, "a") as f:
        f.write(f"{dep.name}: {dep.git_address} {dep.version}\n")

for linkage in ("static", "shared"):
    print("Building final FFmpeg", linkage)
    ffmpeg_builder = FFmpegBuilder(linkage=linkage)
    ffmpeg_builder.build()
    base_dir.chdir()

    with zf.ZipFile(f"{ffmpeg_builder.build_name}.zip", mode="w", compression=zf.ZIP_DEFLATED) as zff:
        for dirname, subdirs, files in os.walk(os.path.join(ffmpeg_builder.build_path, ffmpeg_builder.build_name)):
            zff.write(dirname)
            
            for filename in files:
                zff.write(os.path.join(dirname, filename), compresslevel=9)

        # with open(version_file, "a") as f:
        #     f.write(f"FFmpeg: {ffmpeg_builder.git_address} {ffmpeg_builder.build_name}\n")
        zff.write(version_file, version_file, compresslevel=9)
            