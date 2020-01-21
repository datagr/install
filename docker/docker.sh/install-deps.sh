#!/bin/bash
set -e

# This script will install all the runtime dependencies for the openmpi based flow

yum install -y centos-release-scl
yum install -y epel-release
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum-config-manager --add-repo https://www.opm-project.org/package/opm.repo

yum install -y blas lapack dune-common suitesparse dune-istl dune-geometry dune-grid openmpi trilinos-openmpi ptscotch-openmpi scotch zlib devtoolset-6-toolchain rh-mariadb102-boost

