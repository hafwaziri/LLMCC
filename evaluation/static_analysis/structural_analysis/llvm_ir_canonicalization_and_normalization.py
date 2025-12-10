import tempfile
import subprocess
import os
import re

def canonicalize_and_normalize_ir(llvm_ir):
    tmp_file_path = None
    tmp_output_path = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as tmp_file:
            tmp_file.write(llvm_ir)
            tmp_file_path = tmp_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as tmp_output:
            tmp_output_path = tmp_output.name

        passes = [
            'mem2reg',
            'instcombine',
            'dce',
            'simplifycfg',
            'gvn',
            'loop-simplify',
            'instcombine',
            'simplifycfg',
            'instsimplify'
        ]

        pass_pipeline = ','.join(passes)

        result = subprocess.run(
            ['opt', f'-passes={pass_pipeline}', '--strip-debug', '--strip-named-metadata', '-S', tmp_file_path, '-o', tmp_output_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return False, "", result.stderr

        if not os.path.exists(tmp_output_path):
            return False, "", "opt completed but did not produce an output file."

        with open(tmp_output_path) as f:
            normalized_ir = f.read()

        normalized_ir = re.sub(r'^; ModuleID = .*$\n?', '', normalized_ir, flags=re.MULTILINE)
        normalized_ir = re.sub(r'^source_filename = .*$\n?', '', normalized_ir, flags=re.MULTILINE)
        normalized_ir = re.sub(r'^target datalayout = .*$\n?', '', normalized_ir, flags=re.MULTILINE)
        normalized_ir = re.sub(r'^target triple = .*$\n?', '', normalized_ir, flags=re.MULTILINE)

        return True, normalized_ir, ""

    except subprocess.TimeoutExpired:
        return False, "", "Canonicalization timed out"
    except Exception as e:
        return False, "", f"Error during canonicalization: {str(e)}"
    finally:
        for path in (tmp_file_path, tmp_output_path):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass


if __name__ == "__main__":
    # Example test
    test_ir = """
    define i32 @add(i32 %a, i32 %b) {
      %temp = alloca i32
      store i32 %a, i32* %temp
      %loaded = load i32, i32* %temp
      %result = add i32 %loaded, %b
      ret i32 %result
    }
    """

    success, normalized, error = canonicalize_and_normalize_ir(test_ir)
    print(f"Success: {success}")
    if success:
        print(f"Normalized IR:\n{normalized}")
    else:
        print(f"Error: {error}")
