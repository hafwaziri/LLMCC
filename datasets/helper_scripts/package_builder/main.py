import sys
import subprocess
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import orjson
from tqdm import tqdm
import debugpy

def load_checkpoint(output_dir):
    checkpoint_file = os.path.join(output_dir, ".checkpoint.txt")

    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return set()
    return set()

def append_to_checkpoint(output_dir, package_name):
    checkpoint_file = os.path.join(output_dir, ".checkpoint.txt")
    try:
        with open(checkpoint_file, 'a') as f:
            f.write(f"{package_name}\n")
    except Exception as e:
        print(f"Error appending to checkpoint: {e}")

def is_package_completed(package_name, output_dir):
    output_file = os.path.join(output_dir, f"{package_name}.json")
    if not os.path.exists(output_file):
        return False

    try:
        with open(output_file, 'rb') as f:
            data = orjson.loads(f.read())
            return "name" in data and "source_files" in data
    except:
        return False

def process_package(package_dir, sub_dir, output_dir, processed_packages, cpu_set):

    # debugpy.breakpoint()

    package_path = os.path.abspath(package_dir.path)
    sub_dir_path = os.path.abspath(sub_dir.path)

    package_name = os.path.basename(package_path)
    sub_dir_name = os.path.basename(sub_dir_path)

    if package_name in processed_packages or is_package_completed(package_name, output_dir):
        print(f"Skipping already processed package: {package_name}")
        return True, package_name

    docker_cmd = [
        "docker", "run", "--rm",
        "--cpuset-cpus", cpu_set,
        "-v", f"{package_path}:/worker/{package_name}",
        "-v", f"{sub_dir_path}:/worker/{sub_dir_name}",
        # "-p", "5678:5678",
        "-w", "/worker",
        "debian-builder",
        "python3", "build_worker.py", f"/worker/{package_name}", f"/worker/{sub_dir_name}"
    ]

    print(f"Processing Package: {package_name}")

    try:
        result = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3600
        )
    except subprocess.TimeoutExpired:
        print(f"Package {package_name} timed out after 3600 seconds")
        return False, package_name

    try:
        (build_system, dh_auto_config, dh_auto_build, dh_auto_test, build_stderr, build_returncode,
        test_stdout, test_stderr, test_returncode, test_detected, testing_framework,
        test_stdout_diff, test_stderr_diff, package_viable_for_test_dataset,
        rebuild_stderr, rebuild_returncode, modified_rebuild_stderr, modified_rebuild_returncode,
        test_stdout_for_modified_package, test_stderr_for_modified_package, test_passed ,compilation_data) = orjson.loads(result.stdout)


        package_data = {
            "name": package_name,
            "build_system": build_system,
            "dh_auto_configure": dh_auto_config,
            "dh_auto_build": dh_auto_build,
            "dh_auto_test": dh_auto_test,
            "build_stderr": build_stderr,
            "build_return_code": build_returncode,
            "test_stdout": test_stdout,
            "test_stderr": test_stderr,
            "test_returncode": test_returncode,
            "test_detected": test_detected,
            "testing_framework": testing_framework,
            "test_stdout_diff": test_stdout_diff,
            "test_stderr_diff": test_stderr_diff,
            "package_viable_for_test_dataset": package_viable_for_test_dataset,
            "rebuild_stderr": rebuild_stderr,
            "rebuild_returncode": rebuild_returncode,
            "modified_rebuild_stderr": modified_rebuild_stderr,
            "modified_rebuild_returncode": modified_rebuild_returncode,
            "test_stdout_for_modified_package": test_stdout_for_modified_package,
            "test_stderr_for_modified_package": test_stderr_for_modified_package,
            "test_passed": test_passed,
            "source_files": [
                {
                    "file_path": comp_info['source_file'],
                    "package_name": package_name,
                    "compilation_command": ' '.join(comp_info['compiler_flags']),
                    "output_file": comp_info['output_file'],
                    "src_functions": comp_info['source_functions'],
                    "ir_functions": comp_info['ir_functions'],
                    "random_function": comp_info['random_function'],
                    "random_function_mangled": comp_info['random_function_mangled'],
                    "IR_generation_return_code": comp_info['ir_generation_return_code'],
                    "LLVM_IR": comp_info['llvm_ir'],
                    "IR_generation_stderr": comp_info['ir_generation_stderr'],
                    "random_function_IR_generation_return_code": comp_info['random_func_ir_generation_return_code'],
                    "random_function_IR": comp_info['random_func_llvm_ir'],
                    "random_function_IR_stderr": comp_info['random_func_ir_generation_stderr'],
                    "object_file_generation_return_code": comp_info['object_file_generation_return_code'],
                    "timestamp_check": comp_info['timestamp_check'],
                    "relinked_llvm_ir": comp_info['relinked_llvm_ir'],
                    "modified_object_file_generation_return_code": comp_info['modified_object_file_generation_return_code'],
                    "modified_object_file_timestamp_check": comp_info['modified_object_file_timestamp_check']
                }
                for comp_info in compilation_data
            ]
        }

        output_file = os.path.join(output_dir, f"{package_name}.json")
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'wb') as f:
            f.write(orjson.dumps(package_data, option=orjson.OPT_INDENT_2))

        return True, package_name
    except orjson.JSONDecodeError as e:
        print(f"JSON decode error for {package_name}: {e}")
        print(f"Raw output: {result.stdout!r}")
        return False, package_name
    except Exception as e:
        print(f"Exception in package: {package_name}: {e}")
        return False, package_name

def traverse_dir(root, output_dir, batch_size=None):

    processed_packages = load_checkpoint(output_dir)
    print(f"Loaded {len(processed_packages)} processed packages from checkpoint.")

    packages = []
    dirs = [d for d in os.scandir(root) if d.is_dir()]

    for dir in dirs:
        for sub_dir in os.scandir(dir.path):
            if sub_dir.is_dir():
                package_name = os.path.basename(dir.path)
                if package_name not in processed_packages and not is_package_completed(package_name, output_dir):
                    packages.append((dir, sub_dir))
                break

    if batch_size is not None:
        packages = packages[:batch_size]
        print(f"Batch size limit: {batch_size}. Processing {len(packages)} packages.")
    else:
        print(f"Found {len(packages)} packages to process.")

    if not packages:
        print("No packages to process. Exiting.")
        return

    # Dynamically generate CPU assignments
    total_cpus = multiprocessing.cpu_count()
    reserved_cpus = 4
    cores_per_worker = 2
    available_cpus = total_cpus - reserved_cpus
    max_workers = available_cpus // cores_per_worker

    cpu_assignments = [
        f"{i},{i+1}"
        for i in range(0, max_workers * cores_per_worker, cores_per_worker)
    ]

    print(f"Total CPUs: {total_cpus}")
    print(f"Reserved: {reserved_cpus}")
    print(f"Using {max_workers} workers with {cores_per_worker} cores each.")
    print(f"CPU Assignments: {cpu_assignments}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = []
        for i, (dir, sub_dir) in enumerate(packages):
            cpu_set = cpu_assignments[i % len(cpu_assignments)]
            future = executor.submit(
                process_package,
                dir,
                sub_dir,
                output_dir,
                processed_packages,
                cpu_set
            )
            futures.append(future)

        results = []
        for future in tqdm(
            as_completed(futures),
            total=len(packages),
            desc="Processing packages"
        ):
            success, package_name = future.result()
            results.append(success)

            if success:
                processed_packages.add(package_name)
                append_to_checkpoint(output_dir, package_name)

def main():

    if len(sys.argv) < 3:
        print("Usage: python script.py <root_directory> <output_directory> [--batch-size N] [--force-reprocess]")
        sys.exit(1)
    root_dir = sys.argv[1]
    output_dir = sys.argv[2]
    force_reprocess = "--force-reprocess" in sys.argv

    batch_size = None
    if "--batch-size" in sys.argv:
        batch_index = sys.argv.index("--batch-size") + 1
        batch_size = int(sys.argv[batch_index])

    if force_reprocess:
        checkpoint_file = os.path.join(output_dir, ".checkpoint.txt")
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
        print("Force reprocess enabled. Checkpoint cleared.")

    traverse_dir(root_dir, output_dir, batch_size)

if __name__ == "__main__":
    # debugpy.listen(("0.0.0.0", 5690))
    # debugpy.wait_for_client()

    main()
