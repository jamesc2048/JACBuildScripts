from build_base import BuilderBase

import os

class FFmpegBuilder(BuilderBase):
    def __init__(self, linkage):
        super().__init__("ffmpeg", "https://github.com/FFmpeg/FFmpeg.git", linkage)

        self.linkage = linkage

    def build(self):
        self.update_sources()
        self.build_path.mkdir()
        self.build_path.chdir()

        configure_options = [
                            "--disable-autodetect",
                            "--enable-nonfree",
                            "--enable-gpl",
                            "--enable-version3",
                            "--enable-w32threads",
                            "--prefix=install",
                            "--enable-lto",
                            # Libs
                            "--enable-libx264",
                            "--enable-libx265",
                            "--enable-libsvtav1",
                            "--enable-sdl2",
                            "--enable-opengl",
                            "--enable-dxva2",
                            "--enable-d3d11va",
                            # for correct static link of libraries
                            "--extra-cflags=\"\"-static-libgcc -static-libstdc++\"\"", 
                            "--extra-cxxflags=\"\"-static-libgcc -static-libstdc++\"\"", 
                            "--extra-ldflags=\"\"-static-libgcc -static-libstdc++\"\"", 
                            "--extra-libs=/mingw64/x86_64-w64-mingw32/lib/libwinpthread.a",
                            "--extra-libs=/mingw64/lib/gcc/x86_64-w64-mingw32/10.2.0/libstdc++.a",
                            ]

        license = "gpl3"

        linkage = self.linkage.lower()

        if linkage == "shared":
            build_type = "shared"
            configure_options += [ "--enable-shared", "--disable-static" ]
        elif linkage == "static":
            build_type = "static"
            configure_options += [ "--disable-shared", "--enable-static" ]
        else:
            raise Exception(f"invalid linkage type {self.linkage}")

        build_name = f"{build_type}-{self.version}"
        configure_options.append(f"--extra-version={build_name}")

        build_script = (
            f"../{self.git_clone_path}/configure {' '.join(configure_options)} 2>&1 | tee configureLog.txt",
            f"make -j{self.NUM_CORES} 2>&1 | tee makeLog.txt", 
            "make install 2>&1 | tee installLog.txt", 
            "cp *Log.txt install",
            f"mv install {build_name}",
            f"zip -r {build_name}.zip {build_name}",
            f"mv {build_name}.zip ..",
        )

        self.run_in_msys(build_script, working_dir=self.build_abspath, hide_window=True)

if __name__ == "__main__":
    FFmpegBuilder(linkage="shared").build()