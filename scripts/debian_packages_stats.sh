#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <debian_source_directory> <output_stats_file>"
    echo "  debian_source_directory: Directory containing Debian source packages"
    echo "  output_stats_file: File to write statistics to"
    exit 1
fi

DEBIAN_SOURCE_DIR="$1"
STATS_FILE="$2"

if [[ ! -d "$DEBIAN_SOURCE_DIR" ]]; then
    echo "Error: Debian source directory '$DEBIAN_SOURCE_DIR' does not exist"
    exit 1
fi

c_files=$(find "$DEBIAN_SOURCE_DIR" -type f \( -name "*.c" \))
c_count=$(echo "$c_files" | wc -l)
echo "C source files found: $c_count"

cpp_files=$(find "$DEBIAN_SOURCE_DIR" -type f \( -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o -name "*.C" -o -name "*.c++" \))
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
} > "$STATS_FILE"

total_packages=0

for pkg_dir in "$DEBIAN_SOURCE_DIR"/*/; do
  pkg_name=$(basename "$pkg_dir")

  has_code=$(find "$pkg_dir" -type f \( -name "*.c" -o -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o -name "*.C" -o -name "*.c++" \) -print -quit)

  if [ -n "$has_code" ]; then
    echo "$pkg_name" >> "$STATS_FILE"
    ((total_packages++))
  fi
done

{
  echo ""
  echo "Total packages with C/C++ source files: $total_packages"
} >> "$STATS_FILE"

echo "Found $total_packages packages with C/C++ source files."
echo "Statistics written to '$STATS_FILE'"
