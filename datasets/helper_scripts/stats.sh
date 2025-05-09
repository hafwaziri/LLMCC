#!/bin/bash

stats_file="stats.txt"

c_files=$(find ../debian-source -type f \( -name "*.c" \))
c_count=$(echo "$c_files" | wc -l)
echo "C source files found: $c_count"

cpp_files=$(find ../debian-source -type f \( -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o -name "*.C" -o -name "*.c++" \))
cpp_count=$(echo "$cpp_files" | wc -l)
echo "C++ source files found: $cpp_count"

{
  echo "----------------------------------------"
  echo "C source files found: $c_count"
  echo "C++ source files found: $cpp_count"
  echo "----------------------------------------"
  echo ""
  echo "----------------------------------------"
  echo "Packages containing C or C++ source files"
  echo "----------------------------------------"
  echo ""
} > "$stats_file"

total_packages=0

for pkg_dir in ../debian-source/*/; do
  pkg_name=$(basename "$pkg_dir")

  has_code=$(find "$pkg_dir" -type f \( -name "*.c" -o -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o -name "*.C" -o -name "*.c++" \) -print -quit)

  if [ -n "$has_code" ]; then
    echo "$pkg_name" >> "$stats_file"
    ((total_packages++))
  fi
done

{
  echo ""
  echo "Total packages with C/C++ source files: $total_packages"
} >> "$stats_file"

echo "Found $total_packages packages with C/C++ source files."
