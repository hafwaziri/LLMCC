import os
import sys
import subprocess
import traceback
import json
from debian_package_tester import test_package

#TODO: Remove Magic Numbers

COMMAND_TIMEOUT = 300 #5 mins
BUILD_TIMEOUT = 1200 #20 mins
BUILDDEP_TIMEOUT = 600 #10 mins

def run_dh_command(command, package, no_act=True):
    try:
        if no_act:
            result = subprocess.run([command, "--no-act", "--verbose"],
                                    cwd=package.path,
                                    capture_output=True,
                                    text=True,
                                    shell=False,
                                    timeout=COMMAND_TIMEOUT)
            return result.stdout
        else:
            subprocess.run([command], cwd=package.path, timeout=COMMAND_TIMEOUT)
            return ""
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {str(e)}"

def build_package(package):
    try:
        # Bear also used to capture compilation flags
        result = subprocess.run(["bear", "--", "dpkg-buildpackage", "-b", "-uc", "-us"],
                                cwd=package.path,
                                capture_output=True,
                                text=True,
                                shell=False,
                                timeout=BUILD_TIMEOUT
                                )
        
        return result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "BUILD_TIMEOUT", 1
    except Exception as e:
        return f"BUILD_ERROR: {str(e)}", 1

def detect_build_system(output_txt):
    output_lower = output_txt.lower()
    
    if "cmake" in output_lower:
        return "cmake"
    elif "meson" in output_lower:
        return "meson"
    elif "configure" in output_lower:
        return "autotools"
    elif "makefile.pl" in output_lower:
        return "makemaker"
    elif "qmake" in output_lower:
        return "qmake"
    elif "make" in output_lower and not any(x in output_lower for x in ["cmake", "makefile.pl", "qmake"]):
        return "make"
    return "unknown"

#TODO: Move this to the Dockerfile
def update_apt_sources():
    """
    Updates the APT sources list with Debian bookworm repositories and refreshes the package lists.
    Returns True if successful, False otherwise.
    """
    sources_content = """deb https://deb.debian.org/debian bookworm main non-free-firmware
deb-src https://deb.debian.org/debian bookworm main non-free-firmware

deb https://security.debian.org/debian-security bookworm-security main non-free-firmware
deb-src https://security.debian.org/debian-security bookworm-security main non-free-firmware

deb https://deb.debian.org/debian bookworm-updates main non-free-firmware
deb-src https://deb.debian.org/debian bookworm-updates main non-free-firmware"""

    try:
        with open('/tmp/custom_sources.list', 'w') as f:
            f.write(sources_content)
        
        subprocess.run(["sudo", "cp", "/tmp/custom_sources.list", "/etc/apt/sources.list"], 
                     check=True,
                     timeout=COMMAND_TIMEOUT)
        
        subprocess.run(["sudo", "apt-get", "update"], 
                     check=True,
                     timeout=COMMAND_TIMEOUT,
                     capture_output=True)
        return True
    except Exception as e:
        print(f"Failed to update sources: {e}", file=sys.stderr)
        return False
        
def extract_compilation_commands(package_subdir):
    
    compile_commands_path = os.path.join(package_subdir, "compile_commands.json")

    if not os.path.exists(compile_commands_path):
        return []
    
    with open(compile_commands_path, 'r') as f:
        commands = json.load(f)
    
    compilation_data = []
    
    for cmd in commands:
        file_path = cmd.get('file', '')
        if file_path.endswith(('.c', '.cpp', '.cc', '.cxx', '.C')):
            compilation_info = {
                'source_file': file_path,
                'compiler_flags': cmd.get('arguments', []),
                'output_file': cmd.get('output', '')
            }
            compilation_data.append(compilation_info)
            
    return compilation_data
    
def process_package(package, package_subdir):
    build_system = "unknown"
    dh_auto_build = ""
    dh_auto_test = ""
    build_stderr = ""
    build_returncode = 1
    test_stdout = ""
    test_stderr = ""
    test_returncode = 3 #Custom return code 3 for when tests are not available, or exceptions occur
    test_detected = 0 #0 for no detection, 1 for detection
    testing_framework = ""
    stdout_diff = ""
    stderr_diff = ""
    package_viable_for_test_dataset = 0
    compilation_data = []

    
    try:
        dh_auto_config = run_dh_command("dh_auto_configure", package_subdir)
        
        if not dh_auto_config:
            dh_auto_build = run_dh_command("dh_auto_build", package_subdir)
            build_system = detect_build_system(dh_auto_build)
            
            update_apt_sources()
            
            try:
                subprocess.run(["sudo", "apt-get", "build-dep", package.name, "-y"], 
                             cwd=package_subdir.path, 
                             shell=False, 
                             timeout=BUILDDEP_TIMEOUT,
                             capture_output=True)
            except Exception as e:
                print(f"Build-dep failed: {e}", file=sys.stderr)
            
            build_stderr, build_returncode = build_package(package_subdir)
            
            if build_returncode == 0:
                dh_auto_test = run_dh_command("dh_auto_test", package_subdir)
                
                #TODO: Check if dh_auto_test is empty. Call the function for package testing
                
                if dh_auto_test != "":
                    (test_stdout, test_stderr, test_returncode, test_detected, 
                     testing_framework, stdout_diff, stderr_diff, 
                     package_viable_for_test_dataset) = test_package(package.name, 
                                                                     dh_auto_test, 
                                                                     build_system, 
                                                                     package_subdir)
                # Extract the Compilation Commands for the C and C++ Files
                
                compilation_data = extract_compilation_commands(package_subdir.path)
        
        else:
            build_system = detect_build_system(dh_auto_config)
            
            update_apt_sources()
            
            try:
                subprocess.run(["sudo", "apt-get", "build-dep", package.name, "-y"], 
                             cwd=package_subdir.path, 
                             shell=False, 
                             timeout=BUILDDEP_TIMEOUT,
                             capture_output=True)
            except Exception as e:
                print(f"Build-dep failed: {e}", file=sys.stderr)
            
            build_stderr, build_returncode = build_package(package_subdir)
            
            if build_returncode == 0:
                dh_auto_build = run_dh_command("dh_auto_build", package_subdir)
                dh_auto_test = run_dh_command("dh_auto_test", package_subdir)
                
                
                #TODO: Check if dh_auto_test is empty. Call the function for package testing
                
                if dh_auto_test != "":
                    (test_stdout, test_stderr, test_returncode, test_detected, 
                     testing_framework, stdout_diff, stderr_diff, 
                     package_viable_for_test_dataset) = test_package(package.name, 
                                                                     dh_auto_test, 
                                                                     build_system, 
                                                                     package_subdir)
                    
                # Extract the Compilation Commands for the C and C++ Files
                
                compilation_data = extract_compilation_commands(package_subdir.path)
                
    except Exception as e:
        print(f"Exception in process_package: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        build_stderr = f"PROCESS_ERROR: {str(e)}"
        build_returncode = 1
    
    return (build_system, dh_auto_config, dh_auto_build, dh_auto_test, build_stderr, build_returncode, 
            test_stdout, test_stderr, test_returncode, test_detected, testing_framework, stdout_diff, 
            stderr_diff, package_viable_for_test_dataset, compilation_data)
