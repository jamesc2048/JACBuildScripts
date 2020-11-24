rmdir /S /Q build-4.5-contrib-static
mkdir build-4.5-contrib-static
cd build-4.5-contrib-static

cmake -G "Visual Studio 16 2019" -A Win32 -B "build32" -S "..\opencv-4.5.0" -DBUILD_SHARED_LIBS=no -DBUILD_opencv_world=yes -DCMAKE_INSTALL_PREFIX=install -DWITH_OPENMP=yes -DBUILD_PERF_TESTS=no -DBUILD_TESTS=no -DBUILD_opencv_ts=no -DENABLE_LTO=yes -DOPENCV_ENABLE_NONFREE=yes -DOPENCV_EXTRA_MODULES_PATH="opencv_contrib-4.5.0/modules"

cmake -G "Visual Studio 16 2019" -A x64 -B "build64" -S "..\opencv-4.5.0" -DBUILD_SHARED_LIBS=no -DBUILD_opencv_world=yes -DCMAKE_INSTALL_PREFIX=install -DWITH_OPENMP=yes -DBUILD_PERF_TESTS=no -DBUILD_TESTS=no -DBUILD_opencv_ts=no -DENABLE_LTO=yes -DOPENCV_ENABLE_NONFREE=yes -DOPENCV_EXTRA_MODULES_PATH="../opencv_contrib-4.5.0/modules"

cmake --build build32 --config Release
cmake --build build64 --config Release

cmake --install build32
cmake --install build64