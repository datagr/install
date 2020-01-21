#!/bin/bash
set -e

source /opt/rh/devtoolset-6/enable
source /etc/profile.d/modules.sh
module load mpi/openmpi-x86_64

pushd /build

pushd opm-common
mkdir -p build
pushd build
cmake3 .. \
      -DUSE_MPI=ON \
      -DCMAKE_INSTALL_PREFIX=/install \
      -DUSE_RUNPATH=OFF \
      -DWITH_NATIVE=OFF \
      -DBUILD_TESTING=OFF \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -DBOOST_INCLUDEDIR=/opt/rh/rh-mariadb102/root/usr/include \
      -DBOOST_LIBRARYDIR=/opt/rh/rh-mariadb102/root/usr/lib64
make install -j 4
popd
popd

#-----------------------------------------------------------------

pushd opm-material
mkdir -p build
pushd build
cmake3 .. \
       -DUSE_MPI=ON \
       -DCMAKE_INSTALL_PREFIX=/install \
       -DUSE_RUNPATH=OFF \
       -DWITH_NATIVE=OFF \
       -DBUILD_TESTING=OFF \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_SHARED_LIBS=OFF \
       -DBOOST_INCLUDEDIR=/opt/rh/rh-mariadb102/root/usr/include \
       -DBOOST_LIBRARYDIR=/opt/rh/rh-mariadb102/root/usr/lib64
make install -j 4
popd
popd

#-----------------------------------------------------------------

pushd opm-grid
mkdir -p build
pushd build
cmake3 .. \
       -DUSE_MPI=ON \
       -DCMAKE_INSTALL_PREFIX=/install \
       -DUSE_RUNPATH=OFF \
       -DWITH_NATIVE=OFF \
       -DBUILD_TESTING=OFF \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_SHARED_LIBS=OFF \
       -DBOOST_INCLUDEDIR=/opt/rh/rh-mariadb102/root/usr/include \
       -DBOOST_LIBRARYDIR=/opt/rh/rh-mariadb102/root/usr/lib64 \
       -DZOLTAN_ROOT=/usr/lib64/openmpi \
       -DCMAKE_CXX_FLAGS=-I/usr/include/openmpi-x86_64/trilinos \
       -DZOLTAN_INCLUDE_DIRS=/usr/include/openmpi-x86_64/trilinos \
       -DPTSCOTCH_ROOT=/usr/lib64/openmpi \
       -DPTSCOTCH_INCLUDE_DIR=/usr/include/openmpi-x86_64
make install -j 4
popd
popd

#-----------------------------------------------------------------

pushd opm-models
mkdir -p build
pushd build
cmake3 .. \
       -DUSE_MPI=ON \
       -DCMAKE_INSTALL_PREFIX=/install \
       -DUSE_RUNPATH=OFF \
       -DWITH_NATIVE=OFF \
       -DBUILD_TESTING=OFF \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_SHARED_LIBS=OFF \
       -DBOOST_INCLUDEDIR=/opt/rh/rh-mariadb102/root/usr/include \
       -DBOOST_LIBRARYDIR=/opt/rh/rh-mariadb102/root/usr/lib64 \
       -DZOLTAN_ROOT=/usr/lib64/openmpi \
       -DCMAKE_CXX_FLAGS=-I/usr/include/openmpi-x86_64/trilinos \
       -DZOLTAN_INCLUDE_DIRS=/usr/include/openmpi-x86_64/trilinos \
       -DPTSCOTCH_ROOT=/usr/lib64/openmpi \
       -DPTSCOTCH_INCLUDE_DIR=/usr/include/openmpi-x86_64
make install -j 4
popd
popd

#-----------------------------------------------------------------

pushd opm-simulators
mkdir -p build
pushd build
cmake3 .. \
       -DUSE_MPI=ON \
       -DCMAKE_INSTALL_PREFIX=/install \
       -DUSE_RUNPATH=OFF \
       -DWITH_NATIVE=OFF \
       -DBUILD_TESTING=OFF \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_SHARED_LIBS=OFF \
       -DBOOST_INCLUDEDIR=/opt/rh/rh-mariadb102/root/usr/include \
       -DBOOST_LIBRARYDIR=/opt/rh/rh-mariadb102/root/usr/lib64 \
       -DZOLTAN_ROOT=/usr/lib64/openmpi \
       -DCMAKE_CXX_FLAGS=-I/usr/include/openmpi-x86_64/trilinos \
       -DZOLTAN_INCLUDE_DIRS=/usr/include/openmpi-x86_64/trilinos \
       -DPTSCOTCH_ROOT=/usr/lib64/openmpi \
       -DPTSCOTCH_INCLUDE_DIR=/usr/include/openmpi-x86_64
make install -j 4
popd
popd
