#!/bin/bash

NUM_PACKAGES=$1

SOURCE_DIR="../../../../debian-source" 
DEST_DIR="../pilot/LLMCC/datasets/debian-source"

cd $SOURCE_DIR
PACKAGES=$(ls | shuf -n $NUM_PACKAGES)

for pkg in $PACKAGES; do
  cp -r "$pkg" $DEST_DIR
done