import llvmlite.binding as llvm
import re

try:
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
except Exception:
    pass

def normalize_type(type_str):
    # Remove .0, .1, .2, etc. suffixes from struct type names
    # %struct._IO_FILE.0* -> %struct._IO_FILE*
    return re.sub(r'(%struct\.[a-zA-Z_][a-zA-Z0-9_]*)\.\d+', r'\1', type_str)

def extract_function_info(ir_code):
    functions = []
    try:
        module = llvm.parse_assembly(ir_code)
        for func in module.functions:
            func_type = func.global_value_type
            type_elements = list(func_type.elements)

            return_type = str(type_elements[0]) if type_elements else "void"
            arguments = [str(arg_type) for arg_type in type_elements[1:]] if len(type_elements) > 1 else []

            return_type = normalize_type(return_type)
            arguments = [normalize_type(arg) for arg in arguments]

            function_info = {
                "name": func.name,
                "return_type": return_type,
                "arguments": arguments
            }
            functions.append(function_info)
    except Exception:
        pass
    return functions

def functions_count(ir1, ir2, debug=False):
    try:
        funcs1 = extract_function_info(ir1)
        funcs2 = extract_function_info(ir2)

        count_match = len(funcs1) == len(funcs2)

        def get_sig(f):
            args = ", ".join(f["arguments"])
            return f"{f['return_type']} {f['name']}({args})"

        sigs1 = set(get_sig(f) for f in funcs1)
        sigs2 = set(get_sig(f) for f in funcs2)

        signature_match = sigs1 == sigs2

        if debug:
            print("\n=== DEBUG: Functions in IR1 ===")
            for i, func in enumerate(funcs1, 1):
                print(f"{i}. {func}")
            
            print("\n=== DEBUG: Functions in IR2 ===")
            for i, func in enumerate(funcs2, 1):
                print(f"{i}. {func}")
            
            print("\n=== DEBUG: Signatures in IR1 ===")
            for sig in sorted(sigs1):
                print(f"  {sig}")
            
            print("\n=== DEBUG: Signatures in IR2 ===")
            for sig in sorted(sigs2):
                print(f"  {sig}")
            
            print("\n=== DEBUG: Signatures only in IR1 ===")
            for sig in sorted(sigs1 - sigs2):
                print(f"  {sig}")
            
            print("\n=== DEBUG: Signatures only in IR2 ===")
            for sig in sorted(sigs2 - sigs1):
                print(f"  {sig}")

        return {
            "count_match": count_match,
            "signature_match": signature_match,
            "funcs1_count": len(funcs1),
            "funcs2_count": len(funcs2),
            "matching_signatures": len(sigs1 & sigs2),
            "total_unique_signatures": len(sigs1 | sigs2)
        }

    except Exception as e:
        return {
            "count_match": False,
            "signature_match": False,
            "funcs1_count": 0,
            "funcs2_count": 0,
            "matching_signatures": 0,
            "total_unique_signatures": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    # Example usage
    test_ir1 = r"""


    """

    test_ir2 = r"""

    """

    result = functions_count(test_ir1, test_ir2, debug=True)
    print(f"\n=== RESULTS ===")
    print(f"Count match: {result['count_match']}")
    print(f"Signature match: {result['signature_match']}")
    print(f"Functions in IR1: {result['funcs1_count']}")
    print(f"Functions in IR2: {result['funcs2_count']}")
    print(f"Matching signatures: {result['matching_signatures']}")
    print(f"Total unique signatures: {result['total_unique_signatures']}")