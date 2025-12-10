import tempfile
import subprocess
import os

def verify_ir(llvm_ir):

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as tmp_file:
            tmp_file.write(llvm_ir)
            tmp_file_path = tmp_file.name

        result = subprocess.run(['opt', '-passes=verify', '-S', tmp_file_path, '-o', '/dev/null'],
                            capture_output=True,
                            text=True,
                            timeout=60)

        os.unlink(tmp_file_path)

        if result.returncode == 0:
            return True, "IR verification passed"
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        return False, "Verification timed out"
    except Exception as e:
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        return False, f"Error during verification: {str(e)}"

if __name__ == "__main__":
    # Example test
    test_ir = """
    define i32 @add(i32 %a, i32 %b) {
      %result = add i32 %a, %b
      ret i32 %result
    }
    """
    success, output = verify_ir(test_ir)
    print(f"Success: {success}")
    print(f"Output: {output}")
