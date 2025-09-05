import sys
import subprocess
import json
import os
import sqlite3
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

def process_package(package_dir, sub_dir):

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
         test_stdout_diff, test_stderr_diff, package_viable_for_test_dataset, compilation_data) = json.loads(result.stdout)
        
        with sqlite3.connect('../../debian_source_test.db') as conn_local:
            cursor_local = conn_local.cursor()
            cursor_local.execute("""
                INSERT OR REPLACE INTO packages (
                    name, build_system, dh_auto_configure, dh_auto_build, dh_auto_test,
                    build_stderr, build_return_code, test_stdout, test_stderr, test_returncode,
                    test_detected, testing_framework, test_stdout_diff, test_stderr_diff, package_viable_for_test_dataset
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (package_name, build_system, dh_auto_config, dh_auto_build, dh_auto_test, 
                  build_stderr, build_returncode, test_stdout, test_stderr, test_returncode, test_detected, 
                  testing_framework, test_stdout_diff, test_stderr_diff, package_viable_for_test_dataset))
            conn_local.commit()

            for comp_info in compilation_data:
                cursor_local.execute("""
                    INSERT OR REPLACE INTO source_files (
                        file_path, package_name, compilation_command, output_file, functions, random_function, 
                        IR_generation_return_code, LLVM_IR, IR_generation_stderr
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp_info['source_file'],
                    package_name,
                    ' '.join(comp_info['compiler_flags']),
                    comp_info['output_file'],
                    json.dumps(comp_info['functions']),
                    json.dumps(comp_info['random_function']),
                    comp_info['ir_generation_return_code'],
                    comp_info['llvm_ir'],
                    comp_info['ir_generation_stderr']
                ))

        return True
    except json.JSONDecodeError as e:
        print(f"JSON decode error for {package_name}: {e}")
        print(f"Raw output: {result.stdout!r}")
        return False
    except Exception as e:
        print(f"Exception in package: {package_name}: {e}")
        return False

def traverse_dir(root):

    packages = []
    dirs = [d for d in os.scandir(root) if d.is_dir()]

    for dir in dirs:
        for sub_dir in os.scandir(dir.path):
            if sub_dir.is_dir():
                packages.append((dir, sub_dir))
                break
    
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = []
        for dir, sub_dir in packages:
            future = executor.submit(process_package, dir, sub_dir)
            futures.append(future)
            
        results = []
        for future in tqdm(
            futures,
            total=len(packages),
            desc="Processing packages"
        ):
            results.append(future.result())
        

def main():
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <root_directory>")
        sys.exit(1)
    root_dir = sys.argv[1]
    
    conn = sqlite3.connect('../../debian_source_test.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS packages (
        name TEXT PRIMARY KEY NOT NULL,
        build_system TEXT,
        dh_auto_configure TEXT,
        dh_auto_build TEXT,
        dh_auto_test TEXT,
        build_stderr TEXT,
        build_return_code INTEGER,
        test_stdout TEXT,
        test_stderr TEXT,
        test_returncode INTEGER,
        test_detected INTEGER,
        testing_framework TEXT,
        test_stdout_diff TEXT,
        test_stderr_diff TEXT,
        package_viable_for_test_dataset INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS source_files (
        file_path TEXT,
        package_name TEXT,
        compilation_command TEXT,
        output_file TEXT,
        functions TEXT,
        random_function TEXT,
        IR_generation_return_code INTEGER,
        LLVM_IR TEXT,
        IR_generation_stderr TEXT,
        PRIMARY KEY (package_name, file_path),
        FOREIGN KEY (package_name) REFERENCES packages (name)
    )
    ''')

    conn.commit()
    conn.close()
    
    traverse_dir(root_dir)
    
if __name__ == "__main__":
    main()
