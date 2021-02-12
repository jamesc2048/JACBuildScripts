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

base_dir = Path(__file__).dirname()

for build_dir in (d for d in base_dir.dirs() if d.basename().startswith("build-")):
    print("Delete build dir", build_dir)
    build_dir.rmtree()

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

for linkage in ("static", "shared"):
    print("Building final FFmpeg", linkage)
    ffmpeg_builder = FFmpegBuilder(linkage=linkage)
    ffmpeg_builder.build()
    base_dir.chdir()