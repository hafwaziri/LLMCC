"""
function_extractor.py - Extract C/C++ functions from source files

Description:
    This module provides utilities to parse C/C++ source files and extract
    function definitions suitable for LLVM IR replacement.

Functions:
    extract_functions_from_source() - Parse source file and return function names
    extract_functions_from_ir() - Parse LLVM IR code and return function names
"""

import os
from clang.cindex import CursorKind, Index, TypeKind
import llvmlite.binding as llvm
import cxxfilt

#TODO: See if parsing LLVM IR for function name extraction is better

#Guide for extracting type metadata using the python binding for libclang : https://gregoryszorc.com/blog/2012/05/14/python-bindings-updates-in-clang-3.1/
def extract_function_from_source(source_file, compiler_args=None, build_directory=None):

    if compiler_args is None:
        compiler_args = []

    original_cwd = os.getcwd()

    try:

        if build_directory and os.path.isdir(build_directory):
            os.chdir(build_directory)

        functions = []

        index = Index.create()
        translation_unit = index.parse(source_file, args=compiler_args)

        def traverse_cursor(cursor):

            if cursor.location.file and cursor.location.file.name == source_file:

                if cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
                                CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:

                    result_type = cursor.type.get_result()

                    function_info = {
                        "name": cursor.spelling,
                        "return_type": result_type.spelling if result_type else "void",
                        "arguments": []
                    }

                    for child in cursor.get_children():
                        if child.kind == CursorKind.PARM_DECL:
                            function_info["arguments"].append(child.type.spelling)

                    if not function_info["arguments"] and cursor.type.kind == TypeKind.FUNCTIONNOPROTO:
                        function_info["arguments"] = None

                    functions.append(function_info)


            for child in cursor.get_children():
                traverse_cursor(child)


        traverse_cursor(translation_unit.cursor)

        return functions
    except Exception as e:
        # print(f"Function Extractor error: {e}")
        return []
    finally:
        os.chdir(original_cwd)

def extract_function_from_ir(ir_code):
    try:
        functions = []

        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        module = llvm.parse_assembly(ir_code)

        for func in module.functions:
            if func.is_declaration:
                continue

            func_type = func.type


            if func_type.is_pointer:
                func_type = func_type.element_type


            type_elements = list(func_type.elements)

            function_info = {
                "name": func.name,
                "return_type": str(type_elements[0]) if type_elements else "void",
                "arguments": [str(arg_type) for arg_type in type_elements[1:]] if len(type_elements) > 1 else []
            }

            functions.append(function_info)

        return functions

    except Exception as e:
        # print(f"IR Function Extractor error: {e}")
        return []

def demangle_symbols(functions):
    try:
        demangled_functions = []
        for func in functions:
            demangled_name = cxxfilt.demangle(func['name'])
            demangled_func = func.copy()
            demangled_func['name'] = demangled_name
            demangled_functions.append(demangled_func)
        return demangled_functions
    except Exception as e:
        # print(f"Demangling error: {e}")
        return functions

if __name__ == "__main__":

    source_ir = r'''

'''

    source_path = '/worker/ocaml-dune-2.9.3/_build/default/src/stdune/fcntl_stubs.c'

    # functions = extract_function_from_ir(source_ir)
    functions_2 = extract_function_from_source(source_path)

    # for func in functions:
    #     print(f"Function: {func['name']}")
    #     print(f"  Return type: {func['return_type']}")
    #     print(f"  Arguments: {func['arguments']}")
    #     print()

    # print('#'*50)
    # print("\nAfter Demangling:\n")

    # demangled = demangle_symbols(functions)
    # for func in demangled:
    #     print(f"Function: {func['name']}")
    #     print(f"  Return type: {func['return_type']}")
    #     print(f"  Arguments: {func['arguments']}")
    #     print()

    # print('#'*50)
    print("\nFrom Source File:\n")
    for func in functions_2:
        print(f"Function: {func['name']}")
        print(f"  Return type: {func['return_type']}")
        print(f"  Arguments: {func['arguments']}")
        print()
