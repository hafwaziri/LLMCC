FROM debian:bookworm-slim

# RUN echo "deb https://deb.debian.org/debian bookworm main non-free-firmware" > /etc/apt/sources.list && \
#     echo "deb-src https://deb.debian.org/debian bookworm main non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb https://security.debian.org/debian-security bookworm-security main non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb-src https://security.debian.org/debian-security bookworm-security main non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb https://deb.debian.org/debian bookworm-updates main non-free-firmware" >> /etc/apt/sources.list.d/debian-bookworm.list && \
#     echo "deb-src https://deb.debian.org/debian bookworm-updates main non-free-firmware" >> /etc/apt/sources.list.d/debian-bookworm.list

RUN apt-get update && apt-get install -y \
    build-essential \
    debhelper \
    dpkg-dev \
    devscripts \
    sudo \
    bear \
    python3 \
    #Debugpy for remote debugging
    # python3-debugpy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /worker

COPY build_worker.py process_package.py ./