import os
import sys
import subprocess
import traceback
import json
import time
from debian_package_tester import test_package
from function_extractor import extract_function_from_source, extract_function_from_ir, demangle_symbols
from random_function_selector import random_function_selector
from IR_extractor import generate_ir_for_source_file, generate_ir_for_function
from IR_extractor import generate_ir_output_command
from ir2o import ir_to_o
import debugpy


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
                                    timeout=COMMAND_TIMEOUT,
                                    check=False)
            return result.stdout
        else:
            subprocess.run([command], cwd=package.path, timeout=COMMAND_TIMEOUT,
                        shell=False,
                        check=False)
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
                                timeout=BUILD_TIMEOUT,
                                check=False
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
    elif "make" in output_lower and not any(x in output_lower for x in
                                            ["cmake", "makefile.pl", "qmake"]):
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
                'output_file': cmd.get('output', ''),
                'directory': cmd.get('directory', '')
            }
            compilation_data.append(compilation_info)

    return compilation_data

def ir_processing_for_package(compilation_data):
    for source_file in compilation_data:
        source_file["source_functions"] = None
        source_file["ir_functions"] = None
        source_file["random_function"] = None
        source_file["ir_generation_return_code"] = 3
        source_file["llvm_ir"] = None
        source_file["ir_generation_stderr"] = None
        source_file["random_func_ir_generation_return_code"] = 3
        source_file["random_func_llvm_ir"] = None
        source_file["random_func_ir_generation_stderr"] = None
        source_file["object_file_generation_return_code"] = 3
        source_file["timestamp_check"] = 0

        if (not os.path.exists(source_file["source_file"])
            or not os.path.exists(source_file["directory"])
            or source_file["source_file"].split('/')[-1] in
            ["CMakeCCompilerId.c", "CMakeCXXCompilerId.cpp", "CMakeCCompilerABI.c",
            "CMakeCXXCompilerABI.cpp"]
            or source_file["directory"].split('/')[-1] in ["tests", "test", "t",
                                                        "testing", "unittest",
                                                        "ctest", "check",
                                                        "test-suite", "testsuite",
                                                        "regression"]
            or "test" in source_file["source_file"].split('/')[-1].lower()
            or "testing" in source_file["source_file"].split('/')[-1].lower()):
            continue

        all_clang_flags = source_file["compiler_flags"][1:]
        clang_flags = [flag for flag in all_clang_flags
                       if flag.startswith(("-I", "-D", "-std="))]

        source_file_functions = extract_function_from_source(source_file["source_file"],
                                                            clang_flags,
                                                            source_file["directory"])
        if source_file_functions:
            source_file["source_functions"] = source_file_functions

        if source_file["compiler_flags"]:
            compilation_command = generate_ir_output_command(
                source_file["compiler_flags"])
            if not compilation_command:
                continue

            source_ir = generate_ir_for_source_file(source_file["directory"],
                                                compilation_command)
            if source_ir:
                source_file["ir_generation_return_code"] = source_ir.returncode
                source_file["llvm_ir"] = source_ir.stdout
                source_file["ir_generation_stderr"] = source_ir.stderr

                demangled_to_mangled = {}
                ir_file_functions = extract_function_from_ir(source_ir.stdout)
                if ir_file_functions:
                    demangled_functions = demangle_symbols(ir_file_functions)

                    ir_function_names = [func['name'] for func in ir_file_functions]
                    demangled_function_names = [func['name'] for func in demangled_functions]

                    for original, demangled in zip(ir_function_names, demangled_function_names):
                        demangled_to_mangled[demangled] = original


                    source_file["ir_functions"] = demangled_functions

                source_function_names = [func['name'] for func in source_file["source_functions"]] if source_file["source_functions"] else None
                ir_function_names = [func['name'] for func in source_file["ir_functions"]] if source_file["ir_functions"] else None

                source_function_name, ir_function_name = random_function_selector(
                    source_function_names,
                    ir_function_names
                    )

                if source_function_name and ir_function_name:
                    random_function_dict = None
                    if source_file["source_functions"]:
                        for func in source_file["source_functions"]:
                            if func['name'] == source_function_name:
                                random_function_dict = func
                                break
                    source_file["random_function"] = random_function_dict

                if (source_ir.returncode == 0
                    and source_ir.stdout and source_file["random_function"]):
                    mangled_function_name = demangled_to_mangled.get(ir_function_name,
                                                                    ir_function_name)
                    function_ir = generate_ir_for_function(source_ir.stdout,
                                                        mangled_function_name)
                    if function_ir:
                        source_file["random_func_ir_generation_return_code"] = (
                            function_ir.returncode)
                        source_file["random_func_llvm_ir"] = function_ir.stdout
                        source_file["random_func_ir_generation_stderr"] = function_ir.stderr

                if (source_ir.returncode == 0
                    and source_ir.stdout
                    and source_file["output_file"]
                    and os.path.exists(source_file["output_file"])):

                    original_mtime = os.path.getmtime(source_file["output_file"])

                    compilation_command_for_o = source_file["compiler_flags"].copy()
                    compilation_command_for_o[0] = "clang"

                    time.sleep(0.1) #Ensure timestamp difference

                    object_file_generation_result = ir_to_o(
                        source_ir.stdout,
                        compilation_command_for_o,
                        source_file["output_file"],
                        source_file["directory"]
                    )

                    source_file["object_file_generation_return_code"] = (
                        object_file_generation_result.returncode
                    )

                    if os.path.exists(source_file["output_file"]):
                        new_mtime = os.path.getmtime(source_file["output_file"])
                        source_file["timestamp_check"] = new_mtime > original_mtime


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
                            capture_output=True,
                            check=False)
            except Exception as e:
                print(f"Build-dep failed: {e}", file=sys.stderr)

            build_stderr, build_returncode = build_package(package_subdir)

            if build_returncode == 0:
                dh_auto_test = run_dh_command("dh_auto_test", package_subdir)

                if dh_auto_test != "":
                    (test_stdout, test_stderr, test_returncode, test_detected,
                    testing_framework, stdout_diff, stderr_diff,
                    package_viable_for_test_dataset) = test_package(package.name,
                                                                    dh_auto_test,
                                                                    build_system,
                                                                    package_subdir)

                compilation_data = extract_compilation_commands(package_subdir.path)

                if compilation_data:
                    compilation_data = ir_processing_for_package(compilation_data)

        else:
            build_system = detect_build_system(dh_auto_config)

            update_apt_sources()

            try:
                subprocess.run(["sudo", "apt-get", "build-dep", package.name, "-y"],
                            cwd=package_subdir.path,
                            shell=False,
                            timeout=BUILDDEP_TIMEOUT,
                            capture_output=True,
                            check=False)
            except Exception as e:
                print(f"Build-dep failed: {e}", file=sys.stderr)

            build_stderr, build_returncode = build_package(package_subdir)

            if build_returncode == 0:
                dh_auto_build = run_dh_command("dh_auto_build", package_subdir)
                dh_auto_test = run_dh_command("dh_auto_test", package_subdir)

                if dh_auto_test != "":
                    (test_stdout, test_stderr, test_returncode, test_detected,
                    testing_framework, stdout_diff, stderr_diff,
                    package_viable_for_test_dataset) = test_package(package.name,
                                                                    dh_auto_test,
                                                                    build_system,
                                                                    package_subdir)

                compilation_data = extract_compilation_commands(package_subdir.path)

                if compilation_data:
                    compilation_data = ir_processing_for_package(compilation_data)

    except Exception as e:
        print(f"Exception in process_package: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        build_stderr = f"PROCESS_ERROR: {str(e)}"
        build_returncode = 1

    return (build_system, dh_auto_config, dh_auto_build, dh_auto_test, build_stderr,
            build_returncode, test_stdout, test_stderr, test_returncode, test_detected,
            testing_framework, stdout_diff, stderr_diff, package_viable_for_test_dataset,
            compilation_data)
