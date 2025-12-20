import subprocess

def run_executable(executable_path, timeout=60):
    try:
        result = subprocess.run(
            [executable_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return True, result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return False, None, "Execution timed out", None
    except Exception as e:
        return False, None, str(e), None

def io_test(ref_ir_exec, tgt_ir_exec, timeout):
    ref_success, ref_stdout, ref_stderr, ref_returncode = run_executable(ref_ir_exec, timeout)
    tgt_success, tgt_stdout, tgt_stderr, tgt_returncode = run_executable(tgt_ir_exec, timeout)

    return {
        'both_executed': ref_success and tgt_success,
        'stdout_match': ref_stdout == tgt_stdout if (ref_success and tgt_success) else False,
        'stderr_match': ref_stderr == tgt_stderr if (ref_success and tgt_success) else False,
        'returncode_match': ref_returncode == tgt_returncode if (ref_success and tgt_success) else False,
        'reference_output': {
            'success': ref_success,
            'stdout': ref_stdout,
            'stderr': ref_stderr,
            'returncode': ref_returncode
        },
        'target_output': {
            'success': tgt_success,
            'stdout': tgt_stdout,
            'stderr': tgt_stderr,
            'returncode': tgt_returncode
        },
        'match': (ref_success and tgt_success and 
                ref_stdout == tgt_stdout and
                ref_stderr == tgt_stderr and
                ref_returncode == tgt_returncode)
    }

if __name__ == "__main__":
    pass