FROM debian:bookworm-slim

# RUN echo "deb https://deb.debian.org/debian bookworm main non-free-firmware" > /etc/apt/sources.list && \
#     echo "deb-src https://deb.debian.org/debian bookworm main non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb https://security.debian.org/debian-security bookworm-security main non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb-src https://security.debian.org/debian-security bookworm-security main non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb https://deb.debian.org/debian bookworm-updates main non-free-firmware" >> /etc/apt/sources.list.d/debian-bookworm.list && \
#     echo "deb-src https://deb.debian.org/debian bookworm-updates main non-free-firmware" >> /etc/apt/sources.list.d/debian-bookworm.list

#Required to get Python2
RUN echo "deb http://archive.debian.org/debian/ stretch contrib main non-free" > /etc/apt/sources.list

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
    #Packages for the testing framework
    golang-go \
    python3-pytest \
    python-is-python3 \
    python2.7 \
    python3-clang \
    #gnustep-devel \
    #gnustep-make \
    #gnustep-common \
    #libobjc-dev \
    #Debugpy for remote debugging
    python3-debugpy \
    && rm -rf /var/lib/apt/lists/*

# Install errcheck Go static analysis tool, for the testing framework
RUN go install github.com/kisielk/errcheck@v1.7.0

WORKDIR /worker

COPY test_framework/debian_package_tester.py package_builder/build_worker.py package_builder/process_package.py test_framework/test_output_parser.py ir_processing/function_extractor.py ir_processing/random_function_selector.py ir_processing/IR_extractor.py /worker/
