set -e

source /opt/rh/devtoolset-7/enable

CMAKE_FLAGS=('-DCMAKE_INSTALL_PREFIX=/install/usr' '-DCMAKE_PREFIX_PATH=/container/install' '-DBUILD_TESTING=OFF' '-DCMAKE_BUILD_TYPE=Release')


pushd /build

pushd opm-common
mkdir -p build
pushd build
cmake .. "${CMAKE_FLAGS[@]}"
make install -j 16
popd
popd


pushd opm-material
mkdir -p build
pushd build
cmake .. "${CMAKE_FLAGS[@]}"
make install -j 16
popd
popd


pushd opm-grid
mkdir -p build
pushd build
cmake .. "${CMAKE_FLAGS[@]}"
make install -j 16
popd
popd


pushd opm-models
mkdir -p build
pushd build
cmake .. "${CMAKE_FLAGS[@]}"
make install -j 16
popd
popd


pushd opm-simulators
mkdir -p build
pushd build
cmake .. "${CMAKE_FLAGS[@]}"
make install -j 16
popd
popd
