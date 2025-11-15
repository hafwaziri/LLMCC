import os
import sys
import shutil
from pathlib import Path
import orjson
import polars as pl
from tqdm import tqdm

def json_to_parquet(json_dir, output_dir, batch_size=1000):
    json_dir = Path(json_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = list(json_dir.glob('*.json'))
    json_files = [f for f in json_files if not f.name.startswith('.')]

    packages_data = []
    source_files_data = []

    packages_path = output_dir / "packages.parquet"
    source_files_path = output_dir / "source_files.parquet"

    packages_path.unlink(missing_ok=True)
    source_files_path.unlink(missing_ok=True)

    temp_packages_dir = output_dir / "temp_packages"
    temp_sources_dir = output_dir / "temp_sources"
    temp_packages_dir.mkdir(exist_ok=True)
    temp_sources_dir.mkdir(exist_ok=True)

    batch_counter = 0

    for i, json_file in enumerate(tqdm(json_files, desc="Converting JSON to Parquet")):
        try:
            with open(json_file, 'rb') as f:
                data = orjson.loads(f.read())

            if not isinstance(data, dict):
                continue

            package_info = {k: v for k, v in data.items() if k != "source_files"}
            packages_data.append(package_info)

            for source_file in data.get("source_files", []):
                source_file['package_name'] = data['name']
                source_files_data.append(source_file)

            if (i + 1) % batch_size == 0:
                if packages_data:
                    df = pl.DataFrame(packages_data)
                    df.write_parquet(temp_packages_dir / f"batch_{batch_counter}.parquet",
                                    compression="zstd")
                    packages_data.clear()

                if source_files_data:
                    df = pl.DataFrame(source_files_data)
                    df.write_parquet(temp_sources_dir / f"batch_{batch_counter}.parquet",
                                compression="zstd",
                                compression_level=3,
                                row_group_size=1000,
                                data_page_size=256 * 1024)
                    print(f"Written batch {batch_counter}: {i + 1} files processed")
                    source_files_data.clear()

                batch_counter += 1

        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue

    if packages_data:
        df = pl.DataFrame(packages_data)
        df.write_parquet(temp_packages_dir / f"batch_{batch_counter}.parquet",
                        compression="zstd")
        packages_data.clear()

    if source_files_data:
        df = pl.DataFrame(source_files_data)
        df.write_parquet(temp_sources_dir / f"batch_{batch_counter}.parquet",
                    compression="zstd",
                    compression_level=3,
                    row_group_size=1000,
                    data_page_size=256 * 1024)
        source_files_data.clear()
        print(f"Written final batch {batch_counter}")

    print("Merging package batches...")
    package_batches = list(temp_packages_dir.glob("*.parquet"))
    if package_batches:
        pl.concat([pl.scan_parquet(f) for f in package_batches]).sink_parquet(
            packages_path, compression="zstd"
        )

    print("Merging source file batches...")
    source_batches = list(temp_sources_dir.glob("*.parquet"))
    if source_batches:
        pl.concat([pl.scan_parquet(f) for f in source_batches]).sink_parquet(
            source_files_path,
            compression="zstd",
            compression_level=3,
            row_group_size=1000,
            data_page_size=256 * 1024
        )

    shutil.rmtree(temp_packages_dir)
    shutil.rmtree(temp_sources_dir)

    print("Conversion complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python json_to_parquet.py <json_directory> <output_directory> [batch_size]")
        sys.exit(1)

    json_directory = sys.argv[1]
    output_directory = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1000

    json_to_parquet(json_directory, output_directory, batch_size)
