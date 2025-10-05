import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from random_function_selector import random_function_selector

class TestRandomFunctionSelector:

    def test_empty_lists(self):

        source_func, ir_func = random_function_selector([], [])
        assert source_func is None
        assert ir_func is None

    def test_empty_source_functions(self):

        ir_functions = ["add", "multiply", "subtract"]
        source_func, ir_func = random_function_selector([], ir_functions)
        assert source_func is None
        assert ir_func is None

    def test_empty_ir_functions(self):

        source_functions = ["add", "multiply", "subtract"]
        source_func, ir_func = random_function_selector(source_functions, [])
        assert source_func is None
        assert ir_func is None

    def test_simple_matching_functions(self):

        source_functions = ["add", "multiply", "subtract"]
        ir_functions = ["add", "multiply", "subtract"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        assert source_func is not None
        assert ir_func is not None
        assert source_func in source_functions
        assert ir_func in ir_functions

    def test_partial_matching_functions(self):

        source_functions = ["add", "multiply", "divide"]
        ir_functions = ["add", "subtract", "multiply"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        assert source_func is not None
        assert ir_func is not None
        assert source_func in ["add", "multiply"]
        assert ir_func in ["add", "multiply"]

    def test_no_matching_functions(self):

        source_functions = ["add", "multiply", "divide"]
        ir_functions = ["subtract", "modulo", "power"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        assert source_func is None
        assert ir_func is None

    def test_ir_functions_with_parameters(self):

        source_functions = ["add", "multiply", "subtract"]
        ir_functions = ["add(i32, i32)", "multiply(double, double)", "subtract(i32, i32)"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        assert source_func is not None
        assert ir_func is not None
        assert source_func in source_functions
        assert ir_func in ir_functions

    def test_ir_functions_with_namespaces(self):

        source_functions = ["add", "multiply", "calculate"]
        ir_functions = ["std::add", "math::multiply", "Calculator::calculate"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        assert source_func is not None
        assert ir_func is not None
        assert source_func in source_functions

    def test_duplicate_ir_base_names(self):

        source_functions = ["add", "multiply"]
        ir_functions = ["add(i32, i32)", "add(double, double)", "multiply(i32, i32)"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        if source_func is not None:
            assert source_func == "multiply"
            assert "multiply" in ir_func

    def test_single_matching_function(self):

        source_functions = ["unique_function"]
        ir_functions = ["unique_function"]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        assert source_func == "unique_function"
        assert ir_func == "unique_function"

    def test_mixed_complex_scenarios(self):

        source_functions = ["init", "process", "cleanup", "helper"]
        ir_functions = [
            "MyClass::init()",
            "process(i32*, i64)",
            "cleanup",
            "helper(double)",
            "other::process(i32)"
        ]

        source_func, ir_func = random_function_selector(source_functions, ir_functions, random_seed=42)

        if source_func is not None:
            assert source_func in ["init", "cleanup", "helper"]