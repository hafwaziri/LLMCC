FROM debian:trixie-slim

#Required to get Python2
RUN echo "deb http://archive.debian.org/debian/ stretch contrib main non-free" > /etc/apt/sources.list

# Required for build-dep
RUN echo "deb-src http://deb.debian.org/debian trixie main contrib non-free non-free-firmware" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    build-essential \
    clang \
    debhelper \
    dpkg-dev \
    devscripts \
    sudo \
    bear \
    python3 \
    nano \
    llvm \
    llvm-dev \
    #Packages for the testing framework
    golang-go \
    python3-pytest \
    python-is-python3 \
    python2.7 \
    python3-clang \
    python3-pip \
    #gnustep-devel \
    #gnustep-make \
    #gnustep-common \
    #libobjc-dev \
    #Debugpy for remote debugging
    python3-debugpy \
    && rm -rf /var/lib/apt/lists/*

# Install Python Packages
RUN pip install --break-system-packages \
    cxxfilt \
    llvmlite\
    orjson

# Install errcheck Go static analysis tool, for the testing framework
RUN go install github.com/kisielk/errcheck@v1.7.0

WORKDIR /worker

COPY /datasets/helper_scripts/test_framework/debian_package_tester.py \
    /datasets/helper_scripts/package_builder/build_worker.py \
    /datasets/helper_scripts/package_builder/process_package.py \
    /datasets/helper_scripts/test_framework/test_output_parser.py \
    /datasets/helper_scripts/ir_processing/function_extractor.py \
    /datasets/helper_scripts/ir_processing/random_function_selector.py \
    /datasets/helper_scripts/ir_processing/IR_extractor.py \
    /datasets/helper_scripts/ir_processing/nop_injection.py \
    /datasets/helper_scripts/ir_processing/ir2o.py \
    /datasets/helper_scripts/ir_processing/ir_linker.py \
    /datasets/helper_scripts/ir_processing/fix_linkage.py \
    /worker/
