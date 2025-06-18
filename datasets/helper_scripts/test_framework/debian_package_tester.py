import subprocess
import sys
import os
import shlex

TEST_TIMEOUT=1200

def test_package(package_name, dh_auto_test_command, package_build_system, package_subdir):
    
    if '\trm ' in dh_auto_test_command:
        dh_auto_test_command = dh_auto_test_command.split('\trm ')[0].strip()
    dh_auto_test = shlex.split(dh_auto_test_command)
    
    try:
        test_result = subprocess.run(dh_auto_test,
                                    cwd=package_subdir.path,
                                    shell=False,
                                    timeout=TEST_TIMEOUT,
                                    capture_output=True
                                    )
    except Exception as e:
        print(f"Test-Package failed with: {e}", file=sys.stderr)
        
        ###### #TESTING
        
    test_output_file = os.path.join(package_subdir.path, "debian_package_tester_output.txt")
    with open(test_output_file, "w") as f:
        f.write(f"Package: {package_name}\n")
        f.write(f"Build System: {package_build_system}\n")
        f.write(f"Test Output: {test_result}")
            
            
    # file.write(f"Error: {e}\n")
    # if 'test_result' in locals():
        # file.write(f"Return Code: {test_result.returncode}\n")
        # file.write(f"STDOUT:\n{test_result.stdout.decode()}\n")
        # file.write(f"STDERR:\n{test_result.stderr.decode()}\n")