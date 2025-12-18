import subprocess
import os
import tempfile
import sys

def verify_with_alive2(source_ir, target_ir, timeout=600, alive_tv_path='alive-tv'):
    tmp_source = None
    tmp_target = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='_src.ll', delete=False) as f_src:
            f_src.write(source_ir)
            tmp_source = f_src.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='_tgt.ll', delete=False) as f_tgt:
            f_tgt.write(target_ir)
            tmp_target = f_tgt.name

        result = subprocess.run(
            [alive_tv_path, tmp_source, tmp_target],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        stdout = result.stdout
        stderr = result.stderr

        if "Transformation seems to be correct!" in stdout:
            return True, stdout, stderr
        else:
            return False, stdout, stderr

    except subprocess.TimeoutExpired:
        return False, "Verification timed out.", f"Process terminated after {timeout} seconds."
    except Exception as e:
        return False, "", f"An unexpected error occurred: {str(e)}"
    finally:
        for path in (tmp_source, tmp_target):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass



if __name__ == "__main__":
    # Example usage
    source = """
define i32 @add(i32 %x, i32 %y) {
  %sum = add i32 %x, %y
  ret i32 %sum
}
"""

    target = r"""
define i32 @add(i32 %x, i32 %y) {
  %sum = add nsw i32 %x, %y
  ret i32 %sum
}
"""

    print("Verifying with Alive2...\n")
    is_valid, stdout, stderr = verify_with_alive2(
        source,
        target
    )

    if is_valid:
        print("Transformation verified as correct!")
        print("-" * 40)
        print(stdout)
    else:
        print("Transformation is INCORRECT or contains undefined behavior!")
        print("-" * 40)
        if stdout:
            print(stdout)
        else:
            print(f"Error log: {stderr}")