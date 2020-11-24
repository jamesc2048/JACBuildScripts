rmdir /S /Q build-4.5-simple-static
mkdir build-4.5-simple-static
cd build-4.5-simple-static

cmake -G "Visual Studio 16 2019" -A Win32 -B "build32" -S "..\opencv-4.5.0" -DBUILD_SHARED_LIBS=no -DBUILD_opencv_world=yes -DCMAKE_INSTALL_PREFIX=install -DWITH_OPENMP=yes -DENABLE_LTO=yes -DBUILD_PERF_TESTS=no -DBUILD_TESTS=no -DBUILD_opencv_ts=no

cmake -G "Visual Studio 16 2019" -A x64 -B "build64" -S "..\opencv-4.5.0" -DBUILD_SHARED_LIBS=no -DBUILD_opencv_world=yes -DCMAKE_INSTALL_PREFIX=install -DWITH_OPENMP=yes -DENABLE_LTO=yes -DBUILD_PERF_TESTS=no -DBUILD_TESTS=no -DBUILD_opencv_ts=no

cmake --build build32 --config Release
cmake --build build64 --config Release

cmake --install build32
cmake --install build64