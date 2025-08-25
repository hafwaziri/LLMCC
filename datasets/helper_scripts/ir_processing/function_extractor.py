"""
function_extractor.py - Extract C/C++ functions from source files

Description:
    This module provides utilities to parse C/C++ source files and extract
    function definitions suitable for LLVM IR replacement.

Functions:
    extract_functions_from_source() - Parse source file and return function names
"""

from clang.cindex import CursorKind, Index, TypeKind

#TODO: See if parsing LLVM IR for function name extraction is better

#Guide for extracting type metadata using the python binding for libclang : https://gregoryszorc.com/blog/2012/05/14/python-bindings-updates-in-clang-3.1/
def extract_function_from_source(source_file):
    try:
        functions = []

        index = Index.create()
        translation_unit = index.parse(source_file)

        for cursor in translation_unit.cursor.get_children():

            if not cursor.location.file or cursor.location.file.name != source_file:
                continue
            
            if cursor.kind != CursorKind.FUNCTION_DECL:
                continue
            
            result_type = cursor.type.get_result()

            function_info = {
                "name": cursor.spelling,
                "return_type": result_type.kind.spelling,
                "arguments": []
            }
            
            if cursor.type.kind == TypeKind.FUNCTIONNOPROTO:
                function_info["arguments"] = None
            else:
                for arg_type in cursor.type.argument_types():
                    function_info["arguments"].append(arg_type.kind.spelling)

            functions.append(function_info)

        return functions
    except Exception as e:
        print(f"Function Extractor error: {e}")

if __name__ == "__main__":
    source_file_path = ""

    functions = extract_function_from_source(source_file_path)

    for func in functions:
        print(f"Function: {func['name']}")
        print(f"  Return type: {func['return_type']}")
        print(f"  Arguments: {func['arguments']}")
        print()