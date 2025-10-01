import os
import sys
import orjson
import polars as pl
from pathlib import Path
from tqdm import tqdm

def json_to_parquet(json_dir, output_dir):
    json_dir = Path(json_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = list(json_dir.glob('*.json'))

    packages_data = []
    source_files_data = []

    for json_file in tqdm(json_files, desc="Converting JSON to Parquet"):
        try:
            with open(json_file, 'rb') as f:
                data = orjson.loads(f.read())
            package_info = {k: v for k, v in data.items() if k!= "source_files"}
            packages_data.append(package_info)

            for source_file in data.get("source_files", []):
                source_file['package_name'] = data['name']
                source_files_data.append(source_file)
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue

    if packages_data:
        packages_df = pl.DataFrame(packages_data)
        packages_df.write_parquet(output_dir / "packages.parquet", compression="snappy")
        print(f"Written {len(packages_data)} packages to {output_dir / 'packages.parquet'}")

    if source_files_data:
        source_files_df = pl.DataFrame(source_files_data)
        source_files_df.write_parquet(output_dir / "source_files.parquet", compression="snappy")
        print(f"Written {len(source_files_data)} source files to {output_dir / 'source_files.parquet'}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python json_to_parquet.py <json_directory> <output_directory>")
        sys.exit(1)

    json_directory = sys.argv[1]
    output_directory = sys.argv[2]

    json_to_parquet(json_directory, output_directory)
