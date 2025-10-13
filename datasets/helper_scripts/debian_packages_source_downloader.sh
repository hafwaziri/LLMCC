#!/bin/bash

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

    local dest_dir="../debian-source"
    local mirror="deb.debian.org/debian"
    local architecture="source"
    local section="main,contrib,non-free"
    local release="trixie"

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
        "$dest_dir"

    echo "-------------------------------------"
    echo "Download complete!"
    echo "-------------------------------------"

}

check_install_package "debmirror"
download_source
