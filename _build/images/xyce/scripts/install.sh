#!/bin/bash

set -e

git clone --filter=blob:none "${XYCE_REPO_URL}" "${XYCE_NAME}"
export XYCE_DIR=$(readlink -f "${XYCE_NAME}")

cd "${XYCE_DIR}"
git checkout "${XYCE_REPO_COMMIT}"
./bootstrap

git clone --filter=blob:none https://github.com/trilinos/Trilinos trilinos
cd trilinos
git checkout trilinos-release-12-12-1
mkdir -p parallel_build && cd parallel_build
cp ../../../trilinos.reconfigure.sh ./reconfigure.sh
chmod +x reconfigure.sh
./reconfigure.sh
make -j"$(nproc)"
make install

cd "${XYCE_DIR}"
mkdir -p parallel_build && cd parallel_build
cp ../../xyce.reconfigure.sh ./reconfigure.sh
chmod +x reconfigure.sh
./reconfigure.sh
make -j"$(nproc)"
make install
