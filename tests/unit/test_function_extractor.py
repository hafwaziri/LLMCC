import os
import sys
from pathlib import Path
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from function_extractor import (
    extract_function_from_source,
    extract_function_from_ir,
    demangle_symbols
)

class TestExtractFunctionFromSource:

    def test_simple_c_function(self):
        c_code = """
        #include <stdio.h>

        void hello() {
            printf("Hello, World!\\n");
        }

        int add(int a, int b) {
            return a + b;
        }
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            source_file = Path(tmpdirname) / "test.c"
            with open(source_file, 'w') as f:
                f.write(c_code)

            functions = extract_function_from_source(str(source_file))
            expected_functions = [
                {"name": "hello", "return_type": "void", "arguments": None},
                {"name": "add", "return_type": "int", "arguments": ["int", "int"]}
            ]
            assert functions == expected_functions

    def test_cpp_class_methods(self):
        cpp_code = """
class Calculator {
public:
    Calculator();
    ~Calculator();
    int add(int a, int b);
    void reset();
private:
    int value;
};

Calculator::Calculator() : value(0) {}

Calculator::~Calculator() {}

int Calculator::add(int a, int b) {
    value = a + b;
    return value;
}

void Calculator::reset() {
    value = 0;
}

int global_function(const char* str) {
    return strlen(str);
}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write(cpp_code)
            temp_file = f.name

        try:
            functions = extract_function_from_source(temp_file)

            assert len(functions) == 5

            constructor = next((f for f in functions if 'Calculator' in f['name'] and f['return_type'] == ''), None)
            if constructor:
                assert 'Calculator' in constructor['name']

            add_method = next((f for f in functions if f['name'] == 'add'), None)
            assert add_method is not None
            assert add_method['return_type'] == 'int'
            assert add_method['arguments'] == ['int', 'int']

            reset_method = next((f for f in functions if f['name'] == 'reset'), None)
            assert reset_method is not None
            assert reset_method['return_type'] == 'void'

            global_func = next((f for f in functions if f['name'] == 'global_function'), None)
            assert global_func is not None
            assert global_func['return_type'] == 'int'
            assert global_func['arguments'] == ['const char *']

        finally:
            os.unlink(temp_file)

    def test_function_with_complex_types(self):

        c_code = """
#include <stdlib.h>

struct Point {
    int x, y;
};

struct Point* create_point(int x, int y) {
    struct Point* p = malloc(sizeof(struct Point));
    p->x = x;
    p->y = y;
    return p;
}

void process_array(int arr[], size_t count) {
    for (size_t i = 0; i < count; i++) {
        arr[i] *= 2;
    }
}

int (*get_operation(char op))(int, int) {
    return NULL;
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            temp_file = f.name

        try:
            functions = extract_function_from_source(temp_file)

            assert len(functions) == 3

            create_func = next((f for f in functions if f['name'] == 'create_point'), None)
            assert create_func is not None
            assert 'Point' in create_func['return_type']
            assert create_func['arguments'] == ['int', 'int']

            process_func = next((f for f in functions if f['name'] == 'process_array'), None)
            assert process_func is not None
            assert process_func['return_type'] == 'void'
            assert len(process_func['arguments']) == 2

            get_op_func = next((f for f in functions if f['name'] == 'get_operation'), None)
            assert get_op_func is not None
            assert get_op_func['arguments'] == ['char']

        finally:
            os.unlink(temp_file)


    def test_empty_file(self):

        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("")
            temp_file = f.name

        try:
            functions = extract_function_from_source(temp_file)
            assert functions == []
        finally:
            os.unlink(temp_file)

    def test_file_with_only_declarations(self):
        c_code = """
int add(int a, int b);
void print_message(const char* msg);
double calculate(double x, double y);
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            temp_file = f.name

        try:
            functions = extract_function_from_source(temp_file)
            assert len(functions) == 0

        finally:
            os.unlink(temp_file)

class TestExtractFunctionFromIR:

    def test_simple_ir_functions(self):

        ir_code = """
define i32 @add(i32 %a, i32 %b) {
  %result = add i32 %a, %b
  ret i32 %result
}

define void @print_hello() {
  %str = getelementptr [13 x i8], [13 x i8]* @.str, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %str)
  ret void
}

define double @multiply(double %x, double %y) {
  %result = fmul double %x, %y
  ret double %result
}

declare i32 @printf(i8*, ...)

@.str = private unnamed_addr constant [13 x i8] c"Hello World\\0A\\00"
"""
        functions = extract_function_from_ir(ir_code)

        assert len(functions) == 3

        add_func = next((f for f in functions if f['name'] == 'add'), None)
        assert add_func is not None
        assert 'i32' in add_func['return_type']
        assert len(add_func['arguments']) == 2
        assert all('i32' in arg for arg in add_func['arguments'])

        hello_func = next((f for f in functions if f['name'] == 'print_hello'), None)
        assert hello_func is not None
        assert 'void' in hello_func['return_type']
        assert add_func['arguments'] == [] or len(hello_func['arguments']) == 0

        mult_func = next((f for f in functions if f['name'] == 'multiply'), None)
        assert mult_func is not None
        assert 'double' in mult_func['return_type']
        assert len(mult_func['arguments']) == 2

    def test_ir_with_complex_types(self):

        ir_code = """
%struct.Point = type { i32, i32 }

define %struct.Point* @create_point(i32 %x, i32 %y) {
entry:
  %ptr = call i8* @malloc(i64 8)
  %point = bitcast i8* %ptr to %struct.Point*
  %x_ptr = getelementptr %struct.Point, %struct.Point* %point, i32 0, i32 0
  %y_ptr = getelementptr %struct.Point, %struct.Point* %point, i32 0, i32 1
  store i32 %x, i32* %x_ptr
  store i32 %y, i32* %y_ptr
  ret %struct.Point* %point
}

define void @process_array(i32* %arr, i64 %count) {
entry:
  br label %loop

loop:
  %i = phi i64 [0, %entry], [%next_i, %loop]
  %cmp = icmp ult i64 %i, %count
  br i1 %cmp, label %body, label %exit

body:
  %elem_ptr = getelementptr i32, i32* %arr, i64 %i
  %elem = load i32, i32* %elem_ptr
  %doubled = mul i32 %elem, 2
  store i32 %doubled, i32* %elem_ptr
  %next_i = add i64 %i, 1
  br label %loop

exit:
  ret void
}

declare i8* @malloc(i64)
"""
        functions = extract_function_from_ir(ir_code)

        assert len(functions) == 2

        create_func = next((f for f in functions if f['name'] == 'create_point'), None)
        assert create_func is not None
        assert len(create_func['arguments']) == 2

        process_func = next((f for f in functions if f['name'] == 'process_array'), None)
        assert process_func is not None
        assert 'void' in process_func['return_type']
        assert len(process_func['arguments']) == 2

    def test_empty_ir(self):
        """Test extraction from empty IR"""
        functions = extract_function_from_ir("")
        assert functions == []

    def test_ir_with_only_declarations(self):
        """Test extraction from IR with only declarations"""
        ir_code = """
declare i32 @printf(i8*, ...)
declare i8* @malloc(i64)
declare void @free(i8*)
"""
        functions = extract_function_from_ir(ir_code)

        assert functions == []

class TestDemangleSymbols:

    def test_demangle_real_cpp_symbols(self):

        functions = [
            {"name": "_Z3addii", "return_type": "int", "arguments": ["int", "int"]},
            {"name": "_Z11print_hellov", "return_type": "void", "arguments": []},
            {"name": "_ZN10Calculator3addEii", "return_type": "int", "arguments": ["int", "int"]},
            {"name": "main", "return_type": "int", "arguments": ["int", "char**"]},
        ]

        demangled = demangle_symbols(functions)

        assert len(demangled) == 4


        add_func = next((f for f in demangled if 'add' in f['name'] and 'Calculator' not in f['name']), None)
        assert add_func is not None
        assert add_func['name'] != '_Z3addii'

        main_func = next((f for f in demangled if f['name'] == 'main'), None)
        assert main_func is not None
        assert main_func['name'] == 'main'

class TestIntegration:

    def test_source_and_ir_consistency(self):

        c_code = """
int simple_add(int a, int b) {
    return a + b;
}

void do_nothing(void) {
    return;
}
"""

        ir_code = """
define i32 @simple_add(i32 %a, i32 %b) {
entry:
  %result = add i32 %a, %b
  ret i32 %result
}

define void @do_nothing() {
entry:
  ret void
}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            temp_file = f.name

        try:
            source_functions = extract_function_from_source(temp_file)
            ir_functions = extract_function_from_ir(ir_code)


            assert len(source_functions) == len(ir_functions) == 2

            source_names = {f['name'] for f in source_functions}
            ir_names = {f['name'] for f in ir_functions}

            assert 'simple_add' in source_names
            assert 'simple_add' in ir_names
            assert 'do_nothing' in source_names
            assert 'do_nothing' in ir_names

        finally:
            os.unlink(temp_file)

    def test_compiler_args_handling(self):

        c_code = """
#ifdef FEATURE_ENABLED
int feature_function(int x) {
    return x * 2;
}
#endif

int always_present(void) {
    return 42;
}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            temp_file = f.name

        try:
            functions_without = extract_function_from_source(temp_file)

            functions_with = extract_function_from_source(temp_file, ['-DFEATURE_ENABLED'])

            assert len(functions_with) > len(functions_without)

            assert any(f['name'] == 'always_present' for f in functions_without)
            assert any(f['name'] == 'always_present' for f in functions_with)

            assert not any(f['name'] == 'feature_function' for f in functions_without)
            assert any(f['name'] == 'feature_function' for f in functions_with)

        finally:
            os.unlink(temp_file)

    @pytest.mark.skipif(not os.path.exists('/usr/include/stdio.h'), reason="System headers not available")
    def test_with_system_includes(self):

        c_code = """
#include <stdio.h>
#include <string.h>

int string_length(const char* str) {
    return strlen(str);
}

void print_number(int num) {
    printf("Number: %d\\n", num);
}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            temp_file = f.name

        try:
            functions = extract_function_from_source(temp_file)

            assert len(functions) == 2

            function_names = {f['name'] for f in functions}
            assert 'string_length' in function_names
            assert 'print_number' in function_names

            assert 'printf' not in function_names
            assert 'strlen' not in function_names

        finally:
            os.unlink(temp_file)