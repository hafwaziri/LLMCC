import pyarrow.parquet as pq
import sys

def extract_test_passed_packages(input_parquet, output_file):
    table = pq.read_table(input_parquet, columns=['name', 'test_passed'])
    df = table.to_pandas()
    passed_packages = df[df['test_passed'] == 1]['name']

    with open(output_file, 'w') as f:
        for package in passed_packages:
            f.write(f"{package}\n")

    print(f"Extracted {len(passed_packages)} packages that passed tests to {output_file}")

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python extract_test_passed_packages.py <input_parquet> <output_file>")
        sys.exit(1)

    input_parquet = sys.argv[1]
    output_file = sys.argv[2]

    extract_test_passed_packages(input_parquet, output_file)