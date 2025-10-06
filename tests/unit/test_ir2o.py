import os
import sys
import pytest
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from ir2o import ir_to_o

class TestIr2o:

    def test_valid_ir_compilation(self):

        ir = '''
        define i32 @main() {
        entry:
            ret i32 0
        }
        '''
        compilation_command = ["clang", "-c", "-o", "test.o", "placeholder"]
        output_file = "test.o"
        src_directory = "/tmp"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    mock_temp.return_value.__enter__.return_value.name = "/tmp/temp.ll"

                    result = ir_to_o(ir, compilation_command, output_file, src_directory)

                    assert result.returncode == 0
                    mock_run.assert_called_once()
                    mock_unlink.assert_called_once_with("/tmp/temp.ll")

    def test_compilation_failure(self):

        ir = "invalid ir code"
        compilation_command = ["clang", "-c", "-o", "test.o", "placeholder"]
        output_file = "test.o"
        src_directory = "/tmp"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    mock_temp.return_value.__enter__.return_value.name = "/tmp/temp.ll"

                    result = ir_to_o(ir, compilation_command, output_file, src_directory)

                    assert result.returncode == 1
                    mock_unlink.assert_called_once_with("/tmp/temp.ll")

    def test_compilation_command_modification(self):

        ir = "test ir"
        compilation_command = ["clang", "-c", "-o", "test.o", "original_file.ll"]
        output_file = "test.o"
        src_directory = "/tmp"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    temp_name = "/tmp/temp_123.ll"
                    mock_temp.return_value.__enter__.return_value.name = temp_name

                    ir_to_o(ir, compilation_command, output_file, src_directory)

                    call_args = mock_run.call_args
                    actual_command = call_args[0][0]
                    assert actual_command[-1] == temp_name
                    assert actual_command[:-1] == compilation_command[:-1]
                    mock_unlink.assert_called_once_with(temp_name)

    def test_working_directory_used(self):

        ir = "test ir"
        compilation_command = ["clang", "-c", "-o", "test.o", "file.ll"]
        output_file = "test.o"
        src_directory = "/custom/directory"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    mock_temp.return_value.__enter__.return_value.name = "/tmp/temp.ll"

                    ir_to_o(ir, compilation_command, output_file, src_directory)

                    call_args = mock_run.call_args
                    assert call_args[1]['cwd'] == src_directory
                    mock_unlink.assert_called_once_with("/tmp/temp.ll")

    def test_temp_file_content_written(self):

        ir = "define i32 @test() { ret i32 42 }"
        compilation_command = ["clang", "-c", "-o", "test.o", "file.ll"]
        output_file = "test.o"
        src_directory = "/tmp"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    mock_file = MagicMock()
                    mock_temp.return_value.__enter__.return_value = mock_file
                    mock_file.name = "/tmp/temp.ll"

                    ir_to_o(ir, compilation_command, output_file, src_directory)

                    mock_file.write.assert_called_once_with(ir)
                    mock_file.flush.assert_called_once()
                    mock_unlink.assert_called_once_with("/tmp/temp.ll")

    def test_complex_compilation_command(self):

        ir = "test ir"
        compilation_command = [
            "clang",
            "-DLOCALEDIR=\"/usr/share/locale\"",
            "-DHAVE_CONFIG_H",
            "-I.", "-Ilib", "-I./lib",
            "-Wdate-time",
            "-D_FORTIFY_SOURCE=2",
            "-g", "-O2",
            "-c", "-o", "output.o",
            "input.ll"
        ]
        output_file = "output.o"
        src_directory = "/build/dir"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    temp_name = "/tmp/complex_temp.ll"
                    mock_temp.return_value.__enter__.return_value.name = temp_name

                    result = ir_to_o(ir, compilation_command, output_file, src_directory)

                    call_args = mock_run.call_args
                    actual_command = call_args[0][0]

                    assert actual_command[-1] == temp_name
                    assert actual_command[:-1] == compilation_command[:-1]
                    assert result.returncode == 0
                    mock_unlink.assert_called_once_with(temp_name)