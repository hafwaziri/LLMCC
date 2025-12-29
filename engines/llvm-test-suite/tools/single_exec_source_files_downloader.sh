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
    local REPO_URL="https://github.com/llvm/llvm-test-suite.git"
    local TEMP_DIR=$(mktemp -d)

    echo "Cloning llvm-test-suite repository (shallow clone)..."
    git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TEMP_DIR"

    if [ $? -ne 0 ]; then
        echo "Failed to clone repository. Exiting."
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    cd "$TEMP_DIR"
    git sparse-checkout set SingleSource

    if [ $? -ne 0 ]; then
        echo "Failed to checkout SingleSource directory. Exiting."
        cd -
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    echo "Copying source files (.c, .cpp) and headers (.h, .hpp) from SingleSource/..."
    if [ -d "$TEMP_DIR/SingleSource" ]; then
        # Find and copy .c, .cpp, .h, .hpp files while preserving directory structure
        cd "$TEMP_DIR/SingleSource"
        find . -type f \( -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" \) | while read -r file; do
            dir_path=$(dirname "$file")
            mkdir -p "$DEST_DIR/$dir_path"
            cp "$file" "$DEST_DIR/$file"
        done

        echo "Copied $(find "$DEST_DIR" -type f \( -name "*.c" -o -name "*.cpp" \) | wc -l) source files to $DEST_DIR"
        echo "Copied $(find "$DEST_DIR" -type f \( -name "*.h" -o -name "*.hpp" \) | wc -l) header files to $DEST_DIR"
    else
        echo "Warning: SingleSource directory not found in repository"
    fi

    cd -
    echo "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}

check_install_package "git"
download_source

echo "-------------------------------------"
echo "Download complete!"
echo "-------------------------------------"