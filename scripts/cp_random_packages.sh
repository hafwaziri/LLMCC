#!/bin/bash

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <source_directory> <destination_directory> [--clean] [NUM_PACKAGES] [SPECIFIC_PACKAGE]"
    echo "  source_directory: Directory containing source packages"
    echo "  destination_directory: Directory to copy packages to"
    echo "  --clean: Optional flag to clean destination directory first"
    echo "  NUM_PACKAGES: Number of random packages to copy (if no specific package given)"
    echo "  SPECIFIC_PACKAGE: Name of specific package to copy"
fi

SOURCE_DIR="$1"
DEST_DIR="$2"
shift 2

if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist"
    exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
  mkdir "$DEST_DIR"
fi

if [ "$1" = "--clean" ]; then
  rm -rf "${DEST_DIR:?}/"*
  shift # Remove --clean from arguments
fi

cd "$SOURCE_DIR"

if [ -n "$2" ]; then
  if [[ ! -d "$2" ]]; then
    echo "Error: Package '$2' does not exist in source directory"
    exit 1
  fi
  cp -r "$2" "$DEST_DIR"
  echo "Copied specific package '$2' from $SOURCE_DIR to $DEST_DIR"
else
  NUM_PACKAGES=$1
  if [ -n "$NUM_PACKAGES" ]; then
    PACKAGES=$(ls | shuf -n "$NUM_PACKAGES")
    
    for pkg in $PACKAGES; do
      cp -r "$pkg" "$DEST_DIR"
    done
    echo "Copied $NUM_PACKAGES random packages from $SOURCE_DIR to $DEST_DIR"
  else
    echo "Error: Either provide NUM_PACKAGES or SPECIFIC_PACKAGE"
    exit 1
  fi
fi
