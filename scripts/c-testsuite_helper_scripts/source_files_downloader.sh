#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <destination_directory>"
    echo "  destination_directory: Directory to download the source files to"
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
        sudo apt install $package_name

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
    local REPO_URL="https://github.com/c-testsuite/c-testsuite.git"
    local TEMP_DIR=$(mktemp -d)
    
    echo "Cloning c-testsuite repository..."
    git clone --depth 1 "$REPO_URL" "$TEMP_DIR"
    
    if [ $? -ne 0 ]; then
        echo "Failed to clone repository. Exiting."
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    echo "Copying .c files from tests/single-exec/..."
    if [ -d "$TEMP_DIR/tests/single-exec" ]; then
        find "$TEMP_DIR/tests/single-exec" -name "*.c" -exec cp {} "$DEST_DIR/" \;
        echo "Copied $(find "$DEST_DIR" -name "*.c" | wc -l) .c files to $DEST_DIR"
    else
        echo "Warning: tests/single-exec directory not found in repository"
    fi
    
    echo "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}


check_install_package "git"
download_source

echo "-------------------------------------"
echo "Download complete!"
echo "-------------------------------------"