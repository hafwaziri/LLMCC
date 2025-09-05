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
    
    for i, part in enumerate(parts):
        if skip_next:
            skip_next= False
            continue
    
        if part == "-o":
            skip_next = True
            continue
        
        if part == "-c":
            continue
        
        # if part.startswith('-D') and '=' in part:
        #     macro_part, value_part = part.split('=', 1)
        #     if value_part.startswith('"') and value_part.endswith('"'):
        #         value_part = value_part[1:-1]
        #     if '/' in value_part:
        #         part = f'{macro_part}=\\"{value_part}\\"'
        #     else:
        #         part = f'{macro_part}={value_part}'
        
        filtered_parts.append(part)
    
    filtered_parts.extend(["-S", "-emit-llvm", "-o", "-"])
    
    return filtered_parts

def generate_ir_for_source_file(source_path, compilation_command):
    try:
        LLVM_IR = subprocess.run(compilation_command,
                                 cwd=source_path,
                                 shell=False,
                                 capture_output=True,
                                 text=True
                                 )

        return LLVM_IR
    except Exception as e:
        print(f"Generate IR for Source File error: {e}")

def generate_ir_for_function(source_ir, function_name):
    try:
        extract_command = ["llvm-extract", f"-func={function_name}", "-S", "-", "-o", "-"]
        LLVM_IR = subprocess.run(extract_command,
                                 shell=False,
                                 input=source_ir,
                                 capture_output=True,
                                 text=True)
        return LLVM_IR
    except Exception as e:
        print(f"Generate IR for a Function error: {e}")

if __name__ == "__main__":
    # source_file = "./test.c"
    # compilation_command = "clang -S -emit-llvm -o - test.c"
    
    # LLVM_IR = generate_ir_for_source_file(source_file, compilation_command)
    # print(LLVM_IR.stdout)
    
    # functions = extract_function_from_source(source_file)
    # random_function = random_function_selector(functions)
    # print("#"*50)
    # for i, function in enumerate(functions):
    #     print(f"Function: {i}: {function}")
    # print(f"Random Function: {random_function}")
    
    # print("#"*50)
    
    # Function_IR = generate_ir_for_function(LLVM_IR.stdout, random_function['name'])
    # print(Function_IR.stdout)
    
    original_compilation_command = ''''''
    cleaned_comp_command = generate_ir_output_command(original_compilation_command)
    print(cleaned_comp_command)
    
    source_file = ""
    generated_IR = generate_ir_for_source_file(source_file, cleaned_comp_command)
    print(generated_IR)