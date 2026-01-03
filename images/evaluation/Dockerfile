FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    re2c \
    z3 \
    libz3-dev \
    libhiredis-dev \
    python3 \
    python3-pip \
    clang \
    llvm \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip3 install --break-system-packages --no-cache-dir networkx llvmlite orjson argparse

# Build LLVM
RUN mkdir -p /opt/llvm-project && cd /opt/llvm-project && \
    git clone --depth 1 https://github.com/llvm/llvm-project.git llvm && \
    mkdir build && cd build && \
    cmake -GNinja \
        -DLLVM_ENABLE_RTTI=ON \
        -DBUILD_SHARED_LIBS=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DLLVM_ENABLE_ASSERTIONS=ON \
        -DLLVM_ENABLE_PROJECTS="llvm;clang" \
        ../llvm/llvm && \
    ninja

# Build Alive2
RUN cd /opt && \
    git clone https://github.com/AliveToolkit/alive2.git && \
    cd alive2 && \
    mkdir build && cd build && \
    cmake -GNinja \
        -DCMAKE_PREFIX_PATH=/opt/llvm-project/build \
        -DBUILD_TV=1 \
        -DCMAKE_BUILD_TYPE=Release \
        .. && \
    ninja

# Add Alive2 to PATH
ENV PATH="/opt/alive2/build:${PATH}"

WORKDIR /workspace