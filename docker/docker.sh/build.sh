#!/bin/bash
set -e

OPM_COMMON_REF=master
OPM_MATERIAL_REF=master
OPM_GRID_REF=master
OPM_MODELS_REF=master
OPM_SIMULATORS_REF=master

HOST_INSTALL_PREFIX=/tmp/flow-install

#-----------------------------------------------------------------------------------

build_dir=$(mktemp -d -t build-flow-XXXXXX)
pushd $build_dir

git clone https://github.com/opm/opm-common
pushd opm-common
git checkout $OPM_COMMON_REF
popd


git clone https://github.com/opm/opm-material
pushd opm-material
git checkout $OPM_MATERIAL_REF
popd


git clone https://github.com/opm/opm-grid
pushd opm-grid
git checkout $OPM_GRID_REF
popd


git clone https://github.com/opm/opm-models
pushd opm-models
git checkout $OPM_MODELS_REF
popd

git clone https://github.com/opm/opm-simulators
pushd opm-simulators
git checkout $OPM_SIMULATORS_REF
popd

popd

#-----------------------------------------------------------------------------------

docker build -f dockerfiles/build-env -t build-env .
docker build -f dockerfiles/builder -t builder .
mkdir -p $HOST_INSTALL_PREFIX
docker run -v $HOST_INSTALL_PREFIX:/install -v $build_dir:/build -it builder

