import sys
import subprocess
import orjson
import os
import sqlite3
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import debugpy

def process_package(package_dir, sub_dir, output_dir):

    # debugpy.breakpoint()

    package_path = os.path.abspath(package_dir.path)
    sub_dir_path = os.path.abspath(sub_dir.path)

    package_name = os.path.basename(package_path)
    sub_dir_name = os.path.basename(sub_dir_path)

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{package_path}:/worker/{package_name}",
        "-v", f"{sub_dir_path}:/worker/{sub_dir_name}",
        "-v", "../test_framework/tests/output_diff/:/worker/package_tester_output_diff/",
        # "-p", "5678:5678",
        "-w", "/worker",
        "debian-builder",
        "python3", "build_worker.py", f"/worker/{package_name}", f"/worker/{sub_dir_name}"
    ]

    print(f"Processing Package: {package_name}")
    result = subprocess.run(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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

        return True
    except orjson.JSONDecodeError as e:
        print(f"JSON decode error for {package_name}: {e}")
        print(f"Raw output: {result.stdout!r}")
        return False
    except Exception as e:
        print(f"Exception in package: {package_name}: {e}")
        return False

def traverse_dir(root, output_dir):

    packages = []
    dirs = [d for d in os.scandir(root) if d.is_dir()]

    for dir in dirs:
        for sub_dir in os.scandir(dir.path):
            if sub_dir.is_dir():
                packages.append((dir, sub_dir))
                break


    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(process_package, dir, sub_dir, output_dir) for dir, sub_dir in packages]

        results = []
        for future in tqdm(
            as_completed(futures),
            total=len(packages),
            desc="Processing packages"
        ):
            results.append(future.result())


def main():

    if len(sys.argv) < 3:
        print("Usage: python script.py <root_directory> <output_directory>")
        sys.exit(1)
    root_dir = sys.argv[1]
    output_dir = sys.argv[2]

    traverse_dir(root_dir, output_dir)

if __name__ == "__main__":
    # debugpy.listen(("0.0.0.0", 5690))
    # debugpy.wait_for_client()

    main()
