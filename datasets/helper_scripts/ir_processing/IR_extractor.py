"""
IR_extractor.py - 

Description:
    

Functions:

"""
import subprocess
import os
from function_extractor import extract_function_from_source
from random_function_selector import random_function_selector


def generate_ir_for_source_file(source_file, compilation_command):
    try:
        LLVM_IR = subprocess.run(compilation_command,
                                 shell=True,
                                 capture_output=True,
                                 text=True
                                 )

        return LLVM_IR
    except Exception as e:
        print(f"Generate IR Function error: {e}")
        return LLVM_IR

def generate_ir_for_function(source_ir, function_name):
    try:
        extract_command = f"llvm-extract -func={function_name} -S - -o -"
        LLVM_IR = subprocess.run(extract_command,
                                 shell=True,
                                 input=source_ir,
                                 capture_output=True,
                                 text=True)
        return LLVM_IR
    except Exception as e:
        print(f"Generate IR for a Function error: {e}")

if __name__ == "__main__":
    source_file = "./test.c"
    compilation_command = "clang -S -emit-llvm -o - test.c"
    
    LLVM_IR = generate_ir_for_source_file(source_file, compilation_command)
    print(LLVM_IR.stdout)
    
    functions = extract_function_from_source(source_file)
    random_function = random_function_selector(functions)
    print("#"*50)
    for i, function in enumerate(functions):
        print(f"Function: {i}: {function}")
    print(f"Random Function: {random_function}")
    
    print("#"*50)
    
    Function_IR = generate_ir_for_function(LLVM_IR.stdout, random_function['name'])
    print(Function_IR.stdout)