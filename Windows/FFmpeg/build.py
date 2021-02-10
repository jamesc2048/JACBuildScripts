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

from path import Path

# current working dir
base_dir = Path(__file__).dirname()

# TODO shared build

for linkage in ("static", ):
    deps = [
        X264Builder(linkage=linkage),
        X265Builder(linkage=linkage),
        SVTAV1Builder(linkage=linkage),
    ]

    for dep in deps:
        print("Building dep", dep.name)
        
        dep.build()
        base_dir.chdir()

    print("Building final FFmpeg", linkage)
    ffmpeg_builder = FFmpegBuilder(linkage=linkage)
    ffmpeg_builder.build()