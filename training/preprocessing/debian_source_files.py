import sys
import pyarrow.parquet as pq
import random
from pathlib import Path
import json
from training.preprocessing.preprocess import preprocess_llvm_ir

def construct_source_path(debian_packages_path, package_name, file_path):
    relative_path = file_path.replace("/worker/", "", 1)
    return Path(debian_packages_path) / package_name / relative_path

def read_source_code(source_path):
    try:
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return None

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python debian_source_files.py <path_to_debian_packages> <parquet_file> <jsonl_output_path> <test_dataset_packages_file> <test_dataset_output_file>")
        sys.exit(1)

    debian_packages_path = sys.argv[1]
    parquet_file_path = sys.argv[2]
    train_output_path = sys.argv[3]
    test_packages_file = sys.argv[4]
    test_output_path = sys.argv[5]

    test_packages = set()
    try:
        with open(test_packages_file, 'r') as f:
            test_packages = set(line.strip() for line in f if line.strip())
        print(f"Loaded {len(test_packages)} test packages")
    except Exception as e:
        print(f"Warning: Could not read test packages file: {e}")
        print("Continuing without test split...")

    pf = pq.ParquetFile(parquet_file_path)

    total_rows = pf.metadata.num_rows
    print(f"Total rows in Parquet file: {total_rows}")

    columns = ['file_path', 'package_name', 'LLVM_IR', 'IR_generation_return_code']

    train_indices = []
    test_indices = []
    batch_size = 100

    print("Identifying valid rows and splitting into train/test...")

    num_row_groups = pf.num_row_groups
    print(f"Number of row groups: {num_row_groups}")

    current_row = 0


    for rg_idx in range(num_row_groups):
        try:
            row_group = pf.read_row_group(rg_idx, columns=columns)
            pyd = row_group.to_pydict()
            n = row_group.num_rows
            
            for i in range(n):
                try:
                    if pyd['IR_generation_return_code'][i] == 0 and pyd['LLVM_IR'][i] is not None:
                        package_name = pyd['package_name'][i]
                        if package_name in test_packages:
                            test_indices.append(current_row)
                        else:
                            train_indices.append(current_row)
                except Exception as e:
                    print(f"Warning: Error processing row {current_row}: {e}")
                current_row += 1
                
        except Exception as e:
            print(f"Warning: Error reading row group {rg_idx}: {e}")
            print(f"Skipping row group {rg_idx}, continuing with next...")

            if rg_idx < num_row_groups - 1:
                try:
                    rows_in_group = pf.metadata.row_group(rg_idx).num_rows
                    current_row += rows_in_group
                    print(f"Skipped {rows_in_group} rows from corrupted row group")
                except:

                    current_row += batch_size

    print(f"Total train rows found: {len(train_indices)}")
    print(f"Total test rows found: {len(test_indices)}")

    if len(train_indices) == 0 and len(test_indices) == 0:
        print("No valid rows found. Exiting.")
        sys.exit(1)


    random.shuffle(train_indices)
    random.shuffle(test_indices)


    train_indices_set = set(train_indices)
    test_indices_set = set(test_indices)

    print(f"Processing all valid rows...")

    def process_dataset(indices_set, output_path, dataset_name):
        written_count = 0
        current_row = 0

        with open(output_path, 'w') as out:
            for rg_idx in range(num_row_groups):
                try:
                    row_group = pf.read_row_group(rg_idx, columns=columns)
                    pyd = row_group.to_pydict()
                    n = row_group.num_rows

                    for i in range(n):
                        if current_row in indices_set:
                            try:
                                file_path = pyd['file_path'][i]
                                package_name = pyd['package_name'][i]
                                llvm_ir = pyd['LLVM_IR'][i]

                                source_path = construct_source_path(debian_packages_path, package_name, file_path)
                                source_code = read_source_code(source_path)

                                if source_code is None:
                                    print(f"Could not read source code for {source_path}, skipping.")
                                    current_row += 1
                                    continue

                                try:
                                    preprocessed_ir = preprocess_llvm_ir(llvm_ir)
                                except Exception as e:
                                    print(f"Preprocessing error for {file_path}: {e}, skipping.")
                                    current_row += 1
                                    continue

                                if preprocessed_ir is False or preprocessed_ir.strip() == "":
                                    print(f"Preprocessing failed for LLVM IR from {file_path}, skipping.")
                                    current_row += 1
                                    continue

                                entry = {
                                    "source_code": source_code,
                                    "llvm_ir": preprocessed_ir,
                                }

                                out.write(json.dumps(entry, ensure_ascii=False) + "\n")
                                written_count += 1

                                if written_count % 100 == 0:
                                    print(f"[{dataset_name}] Wrote {written_count} entries...")
                            except Exception as e:
                                print(f"[{dataset_name}] Error processing row {current_row}: {e}")
                        
                        current_row += 1

                except Exception as e:
                    print(f"Warning: Error reading row group {rg_idx} during {dataset_name} processing: {e}")
                    print(f"Skipping row group, continuing with next...")

                    try:
                        rows_in_group = pf.metadata.row_group(rg_idx).num_rows
                        current_row += rows_in_group
                    except:
                        current_row += batch_size

        print(f"[{dataset_name}] Successfully wrote {written_count} entries to {output_path}.")
        return written_count


    if train_indices_set:
        print("\nProcessing training dataset...")
        process_dataset(train_indices_set, train_output_path, "TRAIN")

    if test_indices_set:
        print("\nProcessing test dataset...")
        process_dataset(test_indices_set, test_output_path, "TEST")

    print("\nProcessing complete!")