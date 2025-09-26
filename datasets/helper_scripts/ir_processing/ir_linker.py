import tempfile
import subprocess
import os
from fix_linkage import restore_private_linkage

def ir_linker(source_ir, modified_function_ir, function_name):

    try:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.ll', delete=False) as source_file, \
            tempfile.NamedTemporaryFile(mode='w+', suffix='.ll', delete=False) as func_file, \
            tempfile.NamedTemporaryFile(mode='r', suffix='.ll', delete=False) as output_file:

            source_file.write(source_ir)
            source_file.flush()
            func_file.write(modified_function_ir)
            func_file.flush()
            source_file_path = source_file.name
            func_file_path = func_file.name
            output_file_path = output_file.name
            output_file.close()

            extract_command = [
                "llvm-extract",
                "--delete",
                "--func=" + function_name,
                source_file_path,
                "-o",
                source_file_path
            ]
            result = subprocess.run(extract_command)

            if result.returncode != 0:
                return None

            link_command = [
                "llvm-link",
                "-S",
                "--override",
                source_file_path,
                func_file_path,
                "-o",
                output_file_path]
            result = subprocess.run(link_command)

            if result.returncode != 0:
                return None

            with open(output_file_path, 'r') as f:
                merged_ir = f.read()

            merged_ir = restore_private_linkage(source_ir, merged_ir)

            return merged_ir

    except Exception as e:
        return None
    finally:
        for path in [source_file_path, func_file_path, output_file_path]:
            os.remove(path)

if __name__ == "__main__":
    pass
