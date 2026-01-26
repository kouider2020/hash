#!/bin/bash
set -e

# === Update and install Python 3.11 + headers ===
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y \
  python3.11 python3.11-dev python3.11-distutils python3-pip

# === Install build dependencies and ARM64 cross-compiler ===
sudo apt-get install -y \
  cmake ninja-build g++ make \
  qemu-user-static binfmt-support crossbuild-essential-arm64 \
  gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# === Build LIEF for aarch64 ===
git clone https://github.com/lief-project/LIEF.git
cd LIEF
mkdir -p build && cd build

cmake .. \
  -DLIEF_PYTHON_API=ON \
  -DPYTHON_EXECUTABLE=$(which python3.11) \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
  -DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc \
  -DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++

make -j$(nproc)

# Save compiled shared library
cp api/python/_lief.so ../lief-shared-lib.so

# === Package wheel ===
cd ../api/python
python3.11 -m pip install build wheel setuptools
python3.11 -m build --wheel

# === List dist contents ===
echo "Contents of dist/:"
ls -R dist || echo "No dist directory found"

# === Copy artifacts locally ===
mkdir -p ../../artifacts
cp dist/*.whl ../../artifacts/ || echo "No wheel found"
cp -r ../build ../../artifacts/lief-build || echo "Build dir not copied"

echo "Artifacts saved under LIEF/artifacts/"
