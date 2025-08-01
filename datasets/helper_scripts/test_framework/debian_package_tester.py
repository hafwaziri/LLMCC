import subprocess
import sys
import os
import shlex

TEST_TIMEOUT=1200

#def parse_test_results(test_results):

def parse_make_test_output(test_result, test_output_file):
    
    #TODO: Check if tests in a specific buildsystem follow certain patterns (most probably not, because of testing frameworks),
    #See if its better to have different cases for build-systems or testing frameworks (find a way to detect the testing framework).
    # with open(test_output_file, "a") as f:
    #     f.write("\n\n\n\n\n\nTHIS IS A TEST")
    return

def test_package(package_name, dh_auto_test_command, package_build_system, package_subdir):
    
    test_stdout = ""
    test_stderr = ""
    test_returncode = 3
        
    #TODO: Make sure common packages/tools/frameworks for testing are available in the container
    
    test_output_file = os.path.join(package_subdir.path, "debian_package_tester_output.txt")
    
    if '\trm ' in dh_auto_test_command:
        dh_auto_test_command = dh_auto_test_command.split('\trm ')[0].strip()
    # dh_auto_test =shlex.split(dh_auto_test_command)
    
    try:
        if dh_auto_test_command == "":
            raise Exception("Test Command is empty after removing 'rm' directive")
        
        test_result = subprocess.run(dh_auto_test_command,
                                    cwd=package_subdir.path,
                                    shell=True, #changed because of cd (for packages using cmake)
                                    timeout=TEST_TIMEOUT,
                                    capture_output=True,
                                    text=True
                                    )
        
        with open(test_output_file, "a") as f:
            f.write(f"Package: {package_name}\n")
            f.write(f"Build System: {package_build_system}\n")
            f.write(f"Return Code: {test_result.returncode}\n")
            f.write(f"STDOUT:\n{test_result.stdout}\n")
            f.write(f"STDERR:\n{test_result.stderr}\n")
        
        
        test_stdout = test_result.stdout
        test_stderr = test_result.stderr
        test_returncode = test_result.returncode
            
        #TODO: Parse the test outputs for different buildsystems
        
        if package_build_system == "make":
            parse_make_test_output(test_result, test_output_file)
        elif package_build_system == "cmake":
            pass
        elif package_build_system == "meson":
            pass
        elif package_build_system == "autotools":
            pass
        elif package_build_system == "makemaker":
            pass
        elif package_build_system == "qmake":
            pass
        elif package_build_system == "unknown": #Some Unknown Buildsystems still have tests
            pass
            
        
    except Exception as e:
        with open(test_output_file, "a") as f:
            f.write(f"Package: {package_name}\n")
            f.write(f"Build System: {package_build_system}\n")
            f.write(f"Debian-Package-Tester-Error: {e}\n")
        
        test_stderr = f"Test_Exception: {str(e)}"
        test_returncode = 3
    
    return test_stdout, test_stderr, test_returncode
            