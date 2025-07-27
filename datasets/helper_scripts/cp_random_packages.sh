#!/bin/bash

#USAGE: ./cp_random_packages.sh [--clean] [NUM_PACKAGES] [SPECIFIC_PACKAGE]

SOURCE_DIR="../../../../debian-source"
DEST_DIR="../pilot/LLMCC/datasets/debian-source"
cd "$SOURCE_DIR"

if [ ! -d "$DEST_DIR" ]; then
  mkdir "$DEST_DIR"
fi

if [ "$1" = "--clean" ]; then
  rm -rf "${DEST_DIR:?}/"*
  shift # Remove --clean from arguments
fi

if [ -n "$2" ]; then
  cp -r "$2" "$DEST_DIR"
else
  NUM_PACKAGES=$1
  if [ -n "$NUM_PACKAGES" ]; then
    PACKAGES=$(ls | shuf -n "$NUM_PACKAGES")
    
    for pkg in $PACKAGES; do
      cp -r "$pkg" "$DEST_DIR"
    done
  fi
fi
