from build_base import BuilderBase
from path import Path
import os

class SVTAV1Builder(BuilderBase):
    def __init__(self, linkage="static"):
        super().__init__("svtav1", "https://github.com/AOMediaCodec/SVT-AV1", linkage)

    def build(self):
        self.update_sources()

        self.build_path.rmtree(ignore_errors=True)
        self.build_path.mkdir_p()
        self.build_path.chdir()

        configure_options = [ "-DCMAKE_INSTALL_PREFIX=/mingw64" ]

        linkage = self.linkage.lower()

        if linkage == "shared":
            build_type = "shared"
            configure_options.append("-DBUILD_SHARED_LIBS=yes")
        elif linkage == "static":
            build_type = "static"
            configure_options.append("-DBUILD_SHARED_LIBS=no")
        else:
            raise Exception(f"invalid linkage type {self.linkage}")

        build_script = (
            f"cmake ../{self.git_clone_path}/ -G 'MSYS Makefiles' {' '.join(configure_options)} 2>&1 | tee configureLog.txt",
            f"make -j{self.NUM_CORES} 2>&1 | tee makeLog.txt", 
            "make install 2>&1 | tee installLog.txt", 
        )

        print(build_script)

        self.run_in_msys(build_script, working_dir=self.build_abspath, hide_window=True)

if __name__ == "__main__":
    SVTAV1Builder().build()
