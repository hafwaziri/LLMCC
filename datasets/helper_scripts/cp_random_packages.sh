#!/bin/bash

NUM_PACKAGES=$1

cd ../../debian-source
PACKAGES=$(ls | shuf -n $NUM_PACKAGES)

for pkg in $PACKAGES; do
  cp -r "$pkg" "../pilot/debian-source"
done