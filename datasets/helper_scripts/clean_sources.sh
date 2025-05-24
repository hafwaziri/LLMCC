#!/bin/bash

PACKAGES_DIR="../debian-source/"
KEEP_LIST="./stats.txt"

find "$PACKAGES_DIR" -mindepth 1 -maxdepth 1 -type d -print | while read dir; do
    pkg_name=$(basename "$dir")
    if ! grep -q "^${pkg_name}$" "$KEEP_LIST"; then
        rm -rf "$dir"
    fi
done

echo "Unnecessary Packages deleted"