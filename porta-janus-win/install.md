Use vcpkg for install fftw3


cmake -S .. -B . -DCMAKE_INSTALL_PREFIX="../local-install" -DCMAKE_BUILD_TYPE=Debug -DJANUS_PLUGINS_DEBUG=1 -DCMAKE_TOOLCHAIN_FILE="C:/Users/Bryton/vcpkg/scripts/buildsystems/vcpkg.cmake"

cd ..

cmake --build build --config Debug --parallel 8

cmake --install build --config Debug