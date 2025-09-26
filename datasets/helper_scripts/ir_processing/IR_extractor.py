"""
IR_extractor.py - 

Description:
    

Functions:

"""
import subprocess
import os
from function_extractor import extract_function_from_source
from random_function_selector import random_function_selector

def generate_ir_output_command(original_compilation_command):
    if isinstance(original_compilation_command, str):
        parts = original_compilation_command.split()
    elif isinstance(original_compilation_command, list):
        parts = original_compilation_command.copy()
    else:
        raise ValueError("compilation_command must be a string or list")

    parts[0] = "/usr/bin/clang"

    filtered_parts = []
    skip_next = False

    optimization_flags = {"-O0", "-O1", "-O2", "-O3", "-Os", "-Oz", "-Ofast", "-Og"}

    for i, part in enumerate(parts):
        if skip_next:
            skip_next= False
            continue

        if part == "-o":
            skip_next = True
            continue

        if part == "-c":
            continue

        if part in optimization_flags:
            continue

        if part.startswith("-W"):
            continue

        if part.startswith("-f"):
            continue

        filtered_parts.append(part)

    filtered_parts.extend(["-O0", "-S", "-emit-llvm", "-o", "-"])

    return filtered_parts

def generate_ir_for_source_file(source_path, compilation_command):
    try:
        LLVM_IR = subprocess.run(compilation_command,
                                 cwd=source_path,
                                 shell=False,
                                 capture_output=True,
                                 text=True,
                                 check=False
                                 )

        return LLVM_IR
    except Exception as e:
        print(f"Generate IR for Source File error: {e}")

def generate_ir_for_function(source_ir, function_name):
    try:
        extract_command = ["llvm-extract", f"-func={function_name}", "--keep-const-init", "-S", "-", "-o", "-"]
        LLVM_IR = subprocess.run(extract_command,
                                 shell=False,
                                 input=source_ir,
                                 capture_output=True,
                                 text=True,
                                 check=False)
        return LLVM_IR
    except Exception as e:
        print(f"Generate IR for a Function error: {e}")

if __name__ == "__main__":
    original_compilation_command = ''''''
