FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    clang \
    gcc \
    g++ \
    llvm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /dataset

CMD ["tail", "-f", "/dev/null"]