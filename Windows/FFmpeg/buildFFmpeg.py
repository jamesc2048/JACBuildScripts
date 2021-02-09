from build_base import BuilderBase

import os

class FFmpegBuilder(BuilderBase):
    def __init__(self, linkage):
        super().__init__("ffmpeg", "https://github.com/FFmpeg/FFmpeg.git", linkage)

        self.linkage = linkage

    def build(self):
        self.update_sources()

        self.build_path.rmtree(ignore_errors=True)
        self.build_path.mkdir_p()
        self.build_path.chdir()

        configure_options = [
                            "--disable-autodetect",
                            "--enable-nonfree",
                            "--enable-gpl",
                            "--enable-version3",
                            "--enable-w32threads",
                            "--extra-libs=/mingw64/x86_64-w64-mingw32/lib/libwinpthread.a",
                            "--prefix=install",
                            "--enable-libx264",
                            ]

        license = "gpl3"

        linkage = self.linkage.lower()

        if linkage == "shared":
            build_type = "shared"
            configure_options.append("--enable-shared")
            configure_options.append("--disable-static")
        elif linkage == "static":
            build_type = "static"
            configure_options.append("--disable-shared")
            configure_options.append("--enable-static")
        else:
            raise Exception(f"invalid linkage type {self.linkage}")


        build_name = f"{build_type}-{self.version}"
        configure_options.append(f"--extra-version={build_name}")

        build_script = (
            f"../{self.git_clone_path}/configure {' '.join(configure_options)} | tee configureLog.txt",
            f"make -j{self.NUM_CORES} | tee makeLog.txt", 
            "make install" + " | tee installLog.txt", 
            "cp *Log.txt install",
            f"mv install {build_name}",
            f"zip -r {build_name}.zip {build_name}",
            f"mv {build_name}.zip ..",
        )

        self.run_in_msys(build_script, working_dir=self.build_abspath, hide_window=True)

if __name__ == "__main__":
    pass
    #FFmpegBuilder(linkage="static").build()