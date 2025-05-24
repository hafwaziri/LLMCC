#!/bin/bash

cd ../../debian-source
PACKAGES=$(ls | shuf -n 10)

for pkg in $PACKAGES; do
  cp -r "$pkg" "../pilot/debian-source"
done
