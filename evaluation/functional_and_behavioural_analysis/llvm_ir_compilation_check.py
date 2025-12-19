import tempfile
import subprocess
import os

def compilation_check(ir, compilation_command, output_file, src_directory):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as temp_ir:
        temp_ir.write(ir)
        temp_ir.flush()

    compilation_command = compilation_command.copy()
    compilation_command[-1] = temp_ir.name

    result = subprocess.run(
        compilation_command,
        cwd=src_directory,
        check=False
    )

    os.unlink(temp_ir.name)
    return result

if __name__ == "__main__":
    pass