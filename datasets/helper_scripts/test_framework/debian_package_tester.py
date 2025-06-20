import subprocess
import sys
import os
import shlex

TEST_TIMEOUT=1200

def test_package(package_name, dh_auto_test_command, package_build_system, package_subdir):
    
    if '\trm ' in dh_auto_test_command:
        dh_auto_test_command = dh_auto_test_command.split('\trm ')[0].strip()
    dh_auto_test = shlex.split(dh_auto_test_command)
    
    test_output_file = os.path.join(package_subdir.path, "debian_package_tester_output.txt")
    
    try:
        test_result = subprocess.run(dh_auto_test,
                                    cwd=package_subdir.path,
                                    shell=False,
                                    timeout=TEST_TIMEOUT,
                                    capture_output=True
                                    )
        
        with open(test_output_file, "w") as f:
            f.write(f"Package: {package_name}\n")
            f.write(f"Build System: {package_build_system}\n")
            f.write(f"Return Code: {test_result.returncode}\n")
            f.write(f"STDOUT:\n{test_result.stdout.decode()}\n")
            f.write(f"STDERR:\n{test_result.stderr.decode()}\n")
            
        #TODO: Parse the test outputs for different buildsystems
        
    except Exception as e:
        with open(test_output_file, "w") as f:
            f.write(f"Package: {package_name}\n")
            f.write(f"Build System: {package_build_system}\n")
            f.write(f"Debian-Package-Tester-Error: {e}\n")