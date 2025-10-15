#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <debian_source_directory>"
    echo "  debian_source_directory: Directory containing downloaded Debian source packages"
    exit 1
fi

DEBIAN_SOURCE_DIR="$1"

if [[ ! -d "$DEBIAN_SOURCE_DIR" ]]; then
    echo "Error: Debian source directory '$DEBIAN_SOURCE_DIR' does not exist"
    exit 1
fi

process_package() {
    local pkg_dir="$1"
    echo "Processing package: ${pkg_dir}"
    
    cd "$pkg_dir"
    
    for dsc_file in *.dsc; do
        
        echo "  Extracting: $dsc_file"
        
        dpkg-source -x "$dsc_file"
        
        # rm "$dsc_file" *.tar.* *.orig.* *.debian.*
    done
    
    cd ..
}

cd "$DEBIAN_SOURCE_DIR"

rm -rf dists project


if [[ ! -d "dists" && ! -d "project" ]]; then
  echo "Successfully deelted both dists and project directories"
else
  echo "Failed to delete"
fi

find ./pool/main -mindepth 2 -maxdepth 2 -exec mv -t ./ {} + && rm -rf ./pool

echo "Sources in subdirectories moved successfuly"

find ./ -type d -empty -delete

echo "Deleted packages that are emptied after deleting redundant files"

export -f process_package

find . -maxdepth 1 -type d -not -path "." | sort | parallel -j $(nproc) process_package

echo "All packages processed."
