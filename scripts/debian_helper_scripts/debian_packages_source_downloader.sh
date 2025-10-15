#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <destination_directory>"
    echo "  destination_directory: Directory to download Debian source packages to"
    exit 1
fi

DEST_DIR="$1"

if [ ! -d "$DEST_DIR" ]; then
    echo "Creating destination directory: $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

check_install_package() {
    local package_name="$1"

    if ! dpkg -l "$package_name" | grep -q "^ii"; then
        echo "Package $package_name is not installed. Installing..."

        sudo apt update
        sudo apt install debmirror

        if ! dpkg -l "$package_name" | grep -q "^ii"; then
            echo "Failed to install $package_name. Exiting."
            exit 1
        else
            echo "$package_name successfully installed."
        fi
    else
        echo "Package $package_name is already installed."
    fi
}

download_source() {
    local mirror="deb.debian.org/debian"
    local architecture="source"
    local section="main,contrib,non-free"
    local release="trixie"

    echo "Downloading Debian source packages to: $DEST_DIR"

    debmirror \
        --progress \
        --verbose \
        --method=http \
        --host="$mirror" \
        --root="/" \
        --arch="$architecture" \
        --dist="$release" \
        --section="$section" \
        --no-check-gpg \
        --ignore-release-gpg \
        --source \
        "$DEST_DIR"

    echo "-------------------------------------"
    echo "Download complete!"
    echo "-------------------------------------"

}

check_install_package "debmirror"
download_source
