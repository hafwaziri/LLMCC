import argparse
import docker
import os
import json
from pathlib import Path

def find_source_files(dataset_path):
    source_files = []
    for ext in ['*.c', '*.cpp']:
        source_files.extend(Path(dataset_path).rglob(ext))
    return [str(f) for f in source_files]

def compile_to_llvm_ir(container, source_file, dataset_path):
    rel_path = os.path.relpath(source_file, dataset_path)
    container_file_path = f"/dataset/{rel_path}"

    container_dir = os.path.dirname(container_file_path)
    file_name = os.path.basename(container_file_path)

    ext = Path(source_file).suffix.lower()

    extra_flags = []
    if ext == ".c":
        extra_flags = [
            "-std=gnu89",
            "-Wno-error=implicit-function-declaration",
            "-Wno-error=implicit-int",
        ]

    cmd = ["clang", "-S", "-emit-llvm", "-o", "-", *extra_flags, file_name]

    try:
        exec_result = container.exec_run(cmd, demux=True, workdir=container_dir)
        stdout, stderr = exec_result.output

        if exec_result.exit_code != 0:
            err = stderr.decode("utf-8", errors="replace") if stderr else ""
            out = stdout.decode("utf-8", errors="replace") if stdout else ""
            msg = err.strip() or out.strip() or "No output captured"
            print(f"    Exit code: {exec_result.exit_code}")
            print(f"    Compilation error: {msg}")
            return None

        return stdout.decode('utf-8')
    except Exception as e:
        print(f"    Exception: {str(e)}")
        return None

def process_dataset(docker_image, dataset_path, output_file):
    client = docker.from_env()

    dataset_path = os.path.abspath(dataset_path)

    print(f"Starting Docker container from image: {docker_image}")

    container = client.containers.run(
        docker_image,
        command="tail -f /dev/null",
        volumes={dataset_path: {'bind': '/dataset', 'mode': 'ro'}},
        detach=True,
        remove=True
    )

    try:
        print(f"Container started: {container.id[:12]}")
        print(f"Searching for source files in: {dataset_path}")

        source_files = find_source_files(dataset_path)
        print(f"Found {len(source_files)} source files")

        results = []
        success_count = 0

        total_c = 0
        total_cpp = 0
        success_c = 0
        success_cpp = 0

        for idx, source_file in enumerate(source_files, 1):
            rel_path = os.path.relpath(source_file, dataset_path)
            print(f"[{idx}/{len(source_files)}] Processing: {rel_path}")

            ext = Path(source_file).suffix.lower()
            if ext == ".c":
                total_c += 1
            elif ext == ".cpp":
                total_cpp += 1

            try:
                with open(source_file, 'r') as f:
                    source_code = f.read()
            except Exception as e:
                print(f"    Failed to read file: {str(e)}")
                continue

            llvm_ir = compile_to_llvm_ir(container, source_file, dataset_path)

            if llvm_ir:
                results.append({
                    'file_path': rel_path,
                    'src': source_code,
                    'ref_ir': llvm_ir
                })
                success_count += 1
                if ext == ".c":
                    success_c += 1
                elif ext == ".cpp":
                    success_cpp += 1
                print(f"    Successfully compiled")
            else:
                print(f"    Failed to compile")

        print(f"Saving results to: {output_file}")
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

        with open(output_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')

        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"Successfully compiled: {success_count}/{len(source_files)} files")
        print(f"  C files:   {success_c}/{total_c} compiled")
        print(f"  C++ files: {success_cpp}/{total_cpp} compiled")
        print(f"Output saved to: {output_file}")
        print(f"{'='*60}")

    finally:
        print("\nStopping and removing container...")
        container.stop()

def main(args):
    process_dataset(args.docker_image, args.raw_dataset_path, args.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--raw_dataset_path', type=str, required=True)
    parser.add_argument('--docker_image', type=str, required=True)
    parser.add_argument('--output_file', type=str, required=True)

    args = parser.parse_args()

    main(args)