import subprocess
import sys
import os
import shlex
import difflib
import re
import test_output_parser

#TODO: Remove Magic Numbers

TEST_TIMEOUT=1200

TEST_OUTPUT_CLEANING_PATTERNS = [
    r"\b\d+ms\b",
    r"\b\d+\.\d+\s+sec\b",
    r"\b\d+\.\d+s\b",
    r"\b\d+\s+milliseconds\b",
    r"\b\d+\s+ms\b",
    r"\b\d+\.\d+\s+seconds\b",
    r"\b\d+\.\d+e[+-]\d+\s+\w+/\w+\b",
    r"\b\d+\s+wallclock\s+secs\s+\([^)]+\)",
    r"--\s+timestamp\s+:\s+\[\d+\]",
    r"total load average:.*?'",
    r"\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}"
]

def clean_test_output(test_output):
    cleaned = test_output

    for pattern in TEST_OUTPUT_CLEANING_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)

    return cleaned

def run_dh_auto_test_command(dh_auto_test_command, package_subdir):
    test_result = subprocess.run(dh_auto_test_command,
                                    cwd=package_subdir.path,
                                    shell=True, #changed because of cd (for packages using cmake)
                                    timeout=TEST_TIMEOUT,
                                    capture_output=True,
                                    text=True
                                    )
    return test_result

def handle_test_rerun_and_diff(test_stdout, test_stderr, dh_auto_test_command, package_subdir, package_name, test_returncode):
    test_rerun_result = run_dh_auto_test_command(dh_auto_test_command, package_subdir)

    if test_rerun_result.returncode != test_returncode:
        return "", "", 0

    original_stdout_cleaned = clean_test_output(test_stdout)
    original_stderr_cleaned = clean_test_output(test_stderr)
    rerun_stdout_cleaned = clean_test_output(test_rerun_result.stdout)
    rerun_stderr_cleaned = clean_test_output(test_rerun_result.stderr)

    stdout_same = original_stdout_cleaned == rerun_stdout_cleaned
    stderr_same = original_stderr_cleaned == rerun_stderr_cleaned

    if stdout_same and stderr_same:
        return "", "", 1

    stdout_diff = '\n'.join(difflib.unified_diff(
        original_stdout_cleaned.splitlines(keepends=True),
        rerun_stdout_cleaned.splitlines(keepends=True),
        fromfile="original_stdout",
        tofile="modified_stdout",
        lineterm=''
    ))
    stderr_diff = '\n'.join(difflib.unified_diff(
        original_stderr_cleaned.splitlines(keepends=True),
        rerun_stderr_cleaned.splitlines(keepends=True),
        fromfile='original_stderr', 
        tofile='modified_stderr',
        lineterm=''
    ))

    # with open(f"package_tester_output_diff/{package_name}_results.txt", "a") as f:
    #     f.write(f"Original Return Code {test_returncode}, Modified: {test_rerun_result.returncode} \n\n\n")
    #     f.write(f"STDOUT DIFF:\n{stdout_diff}\n\n")
    #     f.write(f"STDERR DIFF:\n{stderr_diff}\n\n")

    return stdout_diff, stderr_diff, 0

def test_package(package_name, dh_auto_test_command, package_build_system, package_subdir):

    test_stdout = ""
    test_stderr = ""
    test_returncode = 3
    test_detected = 0
    framework = ""
    stdout_diff = ""
    stderr_diff = ""
    package_viable_for_test_dataset = 0

    #TODO: Make sure common packages/tools/frameworks for testing are available in the container
    #python3-venv

    #test_output_file = os.path.join(package_subdir.path, "debian_package_tester_output.txt")

    if '\trm ' in dh_auto_test_command:
        dh_auto_test_command = dh_auto_test_command.split('\trm ')[0].strip()
    # dh_auto_test =shlex.split(dh_auto_test_command)

    try:
        if dh_auto_test_command == "":
            raise Exception("Test Command is empty after removing 'rm' directive")

        test_result = run_dh_auto_test_command(dh_auto_test_command, package_subdir)

        test_stdout = test_result.stdout
        test_stderr = test_result.stderr
        test_returncode = test_result.returncode

        #Run Test 2x again, first for sanity check then after injecting the modified LLVM IR (#TODO: Injecting part)
        if test_returncode == 3:
            return test_stdout, test_stderr, test_returncode, test_detected, framework, "", "", 0

        test_detected, framework = test_output_parser.parser(test_stdout, test_stderr)

        if test_detected != 1:
            return test_stdout, test_stderr, test_returncode, test_detected, framework, "", "", 0

        stdout_diff, stderr_diff, package_viable_for_test_dataset = handle_test_rerun_and_diff(test_stdout,
                                                                                            test_stderr,
                                                                                            dh_auto_test_command, 
                                                                                            package_subdir,
                                                                                            package_name,
                                                                                            test_returncode)

    except Exception as e:

        test_stderr = f"Test_Exception: {str(e)}"
        test_returncode = 3

    return (test_stdout, test_stderr, test_returncode, test_detected, framework, stdout_diff, 
            stderr_diff, package_viable_for_test_dataset)