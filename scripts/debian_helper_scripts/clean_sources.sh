#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <packages_directory> <keep_list_file>"
    echo "  packages_directory: Directory containing packages to clean"
    echo "  keep_list_file: File containing list of packages to keep"
    exit 1
fi

PACKAGES_DIR="$1"
KEEP_LIST="$2"

if [[ ! -d "$PACKAGES_DIR" ]]; then
    echo "Error: Packages directory '$PACKAGES_DIR' does not exist"
    exit 1
fi

if [[ ! -f "$KEEP_LIST" ]]; then
    echo "Error: Keep list file '$KEEP_LIST' does not exist"
    exit 1
fi

find "$PACKAGES_DIR" -mindepth 1 -maxdepth 1 -type d -print | while read dir; do
    pkg_name=$(basename "$dir")
    if ! grep -q "^${pkg_name}$" "$KEEP_LIST"; then
        rm -rf "$dir"
    fi
done

echo "Unnecessary packages deleted from $PACKAGES_DIR using keep list $KEEP_LIST"