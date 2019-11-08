CMAKE_FLAGS="-DCMAKE_INSTALL_PREFIX=/install -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release"


pushd /build

pushd opm-common
mkdir -p build
pushd build
cmake .. $CMAKE_FLAGS
make install
popd
popd


pushd opm-material
mkdir -p build
pushd build
cmake .. $CMAKE_FLAGS
make install
popd
popd


pushd opm-models
mkdir -p build
pushd build
cmake .. $CMAKE_FLAGS
make install
popd
popd


pushd opm-simulators
mkdir -p build
pushd build
cmake .. $CMAKE_FLAGS
make install
popd
popd
