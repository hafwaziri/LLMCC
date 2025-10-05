import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from IR_extractor import generate_ir_output_command, generate_ir_for_source_file, generate_ir_for_function

class TestGenerateIrOutputCommand:

    def test_basic_command_conversion(self):

        string_command = "gcc -O2 -Wall -c main.c -o main.o"
        list_command = ["gcc", "-O3", "-Wall", "-c", "main.c", "-o", "main.o"]

        result_string = generate_ir_output_command(string_command)
        result_list = generate_ir_output_command(list_command)

        expected = ["/usr/bin/clang", "main.c", "-O0", "-S", "-emit-llvm", "-o", "-"]
        assert result_string == expected
        assert result_list == expected

    def test_invalid_input_type(self):

        with pytest.raises(ValueError, match="compilation_command must be a string or list"):
            generate_ir_output_command(123)

    def test_flag_removal(self):

        original_command = "gcc -O0 -O1 -O2 -O3 -Os -Oz -Ofast -Og -Wall -Wextra -Werror -fPIC -fstack-protector -c main.c -o executable"
        result = generate_ir_output_command(original_command)

        expected = ["/usr/bin/clang", "main.c", "-O0", "-S", "-emit-llvm", "-o", "-"]
        assert result == expected

    def test_preserves_important_flags_and_complex_scenarios(self):

        original_command = "gcc -O2 -Wall -Wextra -fPIC -I./include -I/usr/include -DDEBUG=1 -DVERSION=2 -c src/main.c -o build/main.o"
        result = generate_ir_output_command(original_command)

        expected = ["/usr/bin/clang", "-I./include", "-I/usr/include", "-DDEBUG=1", "-DVERSION=2", "src/main.c", "-O0", "-S", "-emit-llvm", "-o", "-"]
        assert result == expected

    def test_edge_cases(self):

        empty_command = "gcc"
        minimal_command = ["gcc", "main.c"]

        result_empty = generate_ir_output_command(empty_command)
        result_minimal = generate_ir_output_command(minimal_command)

        expected_empty = ["/usr/bin/clang", "-O0", "-S", "-emit-llvm", "-o", "-"]
        expected_minimal = ["/usr/bin/clang", "main.c", "-O0", "-S", "-emit-llvm", "-o", "-"]

        assert result_empty == expected_empty
        assert result_minimal == expected_minimal


class TestGenerateIrForSourceFile:

    @patch('subprocess.run')
    def test_successful_ir_generation(self, mock_run):
        mock_result = Mock()
        mock_result.stdout = "define i32 @main() { ... }"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        source_path = "/path/to/source"
        compilation_command = ["/usr/bin/clang", "main.c", "-O0", "-S", "-emit-llvm", "-o", "-"]

        result = generate_ir_for_source_file(source_path, compilation_command)

        assert result == mock_result
        mock_run.assert_called_once_with(
            compilation_command,
            cwd=source_path,
            shell=False,
            capture_output=True,
            text=True,
            check=False
        )

    @patch('subprocess.run')
    def test_ir_generation_with_error(self, mock_run):

        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = "error: file not found"
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        source_path = "/path/to/source"
        compilation_command = ["/usr/bin/clang", "nonexistent.c", "-O0", "-S", "-emit-llvm", "-o", "-"]

        result = generate_ir_for_source_file(source_path, compilation_command)

        assert result == mock_result

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_subprocess_exception_handling(self, mock_print, mock_run):
        mock_run.side_effect = Exception("Subprocess failed")

        source_path = "/path/to/source"
        compilation_command = ["/usr/bin/clang", "main.c", "-O0", "-S", "-emit-llvm", "-o", "-"]

        result = generate_ir_for_source_file(source_path, compilation_command)

        assert result is None
        mock_print.assert_called_once_with("Generate IR for Source File error: Subprocess failed")


class TestGenerateIrForFunction:

    @patch('subprocess.run')
    def test_successful_function_extraction(self, mock_run):

        mock_result = Mock()
        mock_result.stdout = "define i32 @add(i32 %a, i32 %b) { ... }"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        source_ir = "define i32 @main() { ... }\ndefine i32 @add(i32 %a, i32 %b) { ... }"
        function_name = "add"

        result = generate_ir_for_function(source_ir, function_name)

        assert result == mock_result
        expected_command = ["llvm-extract", "-func=add", "--keep-const-init", "-S", "-", "-o", "-"]
        mock_run.assert_called_once_with(
            expected_command,
            shell=False,
            input=source_ir,
            capture_output=True,
            text=True,
            check=False
        )

    @patch('subprocess.run')
    def test_function_not_found_and_edge_cases(self, mock_run):

        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = "error: function 'nonexistent' not found"
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        source_ir = "define i32 @main() { ... }"
        function_name = "nonexistent"

        result = generate_ir_for_function(source_ir, function_name)
        assert result == mock_result

        empty_ir = ""
        result_empty = generate_ir_for_function(empty_ir, "main")
        assert result_empty == mock_result

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_llvm_extract_exception_handling(self, mock_print, mock_run):
        mock_run.side_effect = Exception("llvm-extract failed")

        source_ir = "define i32 @main() { ... }"
        function_name = "main"

        result = generate_ir_for_function(source_ir, function_name)

        assert result is None
        mock_print.assert_called_once_with("Generate IR for a Function error: llvm-extract failed")