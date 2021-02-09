from build_base import BuilderBase
from path import Path
import os

class X264Builder(BuilderBase):
    def __init__(self, linkage):
        super().__init__("x264", "https://code.videolan.org/videolan/x264.git", linkage)

    def build(self):
        self.update_sources()

        self.build_path.rmtree(ignore_errors=True)
        self.build_path.mkdir_p()
        self.build_path.chdir()

        configure_options = [ "--prefix=/mingw64" ]

        linkage = self.linkage.lower()

        if linkage == "shared":
            build_type = "shared"
            configure_options.append("--enable-shared")
        elif linkage == "static":
            build_type = "static"
            configure_options.append("--enable-static")
        else:
            raise Exception(f"invalid linkage type {self.linkage}")

        build_script = (
            f"../{self.git_clone_path}/configure {' '.join(configure_options)} | tee configureLog.txt",
            f"make -j{self.NUM_CORES} | tee makeLog.txt", 
            "make install | tee installLog.txt", 
        )

        print(build_script)

        self.run_in_msys(build_script, working_dir=self.build_abspath, hide_window=True)

if __name__ == "__main__":
    X264Builder(linkage="shared").build()
