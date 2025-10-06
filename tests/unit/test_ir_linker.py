import os
import sys
import pytest
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from ir_linker import ir_linker

class TestIrLinker:

    def test_successful_linking(self):

        source_ir = """define i32 @main() {
  %result = call i32 @test_func()
  ret i32 %result
}

define i32 @test_func() {
  ret i32 42
}"""

        modified_function_ir = """define i32 @test_func() {
  ret i32 100
}"""

        function_name = "test_func"
        expected_merged_ir = """define i32 @main() {
  %result = call i32 @test_func()
  ret i32 %result
}

define i32 @test_func() {
  ret i32 100
}"""

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('builtins.open', mock_open(read_data=expected_merged_ir)) as mock_file:
                    with patch('os.path.exists', return_value=True):
                        with patch('os.remove') as mock_remove:
                            with patch('ir_linker.restore_private_linkage', return_value=expected_merged_ir) as mock_restore:

                                mock_source = MagicMock()
                                mock_func = MagicMock()
                                mock_output = MagicMock()

                                mock_source.name = "/tmp/source.ll"
                                mock_func.name = "/tmp/func.ll"
                                mock_output.name = "/tmp/output.ll"

                                mock_temp.side_effect = [
                                    mock_source, mock_func, mock_output
                                ]

                                mock_run.return_value = MagicMock(returncode=0)

                                result = ir_linker(source_ir, modified_function_ir, function_name)

                                assert result == expected_merged_ir
                                assert mock_run.call_count == 2
                                mock_restore.assert_called_once_with(source_ir, expected_merged_ir)

    def test_extract_command_failure(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove') as mock_remove:

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]

                        mock_run.return_value = MagicMock(returncode=1)

                        result = ir_linker(source_ir, modified_function_ir, function_name)

                        assert result is None
                        mock_run.assert_called_once()

    def test_link_command_failure(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove') as mock_remove:

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]

                        mock_run.side_effect = [
                            MagicMock(returncode=0),  # extract success
                            MagicMock(returncode=1)   # link failure
                        ]

                        result = ir_linker(source_ir, modified_function_ir, function_name)

                        assert result is None
                        assert mock_run.call_count == 2

    def test_exception_handling(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = Exception("File creation failed")

            result = ir_linker(source_ir, modified_function_ir, function_name)

            assert result is None

    def test_extract_command_construction(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test_function() { ret i32 1 }"
        function_name = "test_function"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove'):

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.__enter__.return_value = mock_source
                        mock_func.__enter__.return_value = mock_func
                        mock_output.__enter__.return_value = mock_output

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]
                        mock_run.return_value = MagicMock(returncode=1)

                        ir_linker(source_ir, modified_function_ir, function_name)

                        expected_extract_cmd = [
                            "llvm-extract",
                            "--delete",
                            "--func=test_function",
                            "/tmp/source.ll",
                            "-o",
                            "/tmp/source.ll"
                        ]
                        mock_run.assert_called_with(expected_extract_cmd)

    def test_link_command_construction(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove'):

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.__enter__.return_value = mock_source
                        mock_func.__enter__.return_value = mock_func
                        mock_output.__enter__.return_value = mock_output

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]
                        mock_run.side_effect = [
                            MagicMock(returncode=0),
                            MagicMock(returncode=1)
                        ]

                        ir_linker(source_ir, modified_function_ir, function_name)


                        expected_link_cmd = [
                            "llvm-link",
                            "-S",
                            "--override",
                            "/tmp/source.ll",
                            "/tmp/func.ll",
                            "-o",
                            "/tmp/output.ll"
                        ]

                        calls = mock_run.call_args_list
                        assert len(calls) == 2
                        assert calls[1][0][0] == expected_link_cmd

    def test_temp_file_writing(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove'):

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.__enter__.return_value = mock_source
                        mock_func.__enter__.return_value = mock_func
                        mock_output.__enter__.return_value = mock_output

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]
                        mock_run.return_value = MagicMock(returncode=1)

                        ir_linker(source_ir, modified_function_ir, function_name)

                        mock_source.write.assert_called_once_with(source_ir)
                        mock_source.flush.assert_called_once()
                        mock_func.write.assert_called_once_with(modified_function_ir)
                        mock_func.flush.assert_called_once()

    def test_output_file_reading(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"
        merged_content = "merged IR content"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('builtins.open', mock_open(read_data=merged_content)) as mock_file:
                    with patch('os.path.exists', return_value=True):
                        with patch('os.remove'):
                            with patch('ir_linker.restore_private_linkage', return_value=merged_content) as mock_restore:

                                mock_source = MagicMock()
                                mock_func = MagicMock()
                                mock_output = MagicMock()

                                mock_source.__enter__.return_value = mock_source
                                mock_func.__enter__.return_value = mock_func
                                mock_output.__enter__.return_value = mock_output

                                mock_source.name = "/tmp/source.ll"
                                mock_func.name = "/tmp/func.ll"
                                mock_output.name = "/tmp/output.ll"

                                mock_temp.side_effect = [mock_source, mock_func, mock_output]
                                mock_run.return_value = MagicMock(returncode=0)

                                result = ir_linker(source_ir, modified_function_ir, function_name)

                                mock_file.assert_called_with("/tmp/output.ll", 'r')
                                assert result == merged_content

    def test_restore_private_linkage_called(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"
        merged_ir = "merged IR"
        restored_ir = "restored IR"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('builtins.open', mock_open(read_data=merged_ir)):
                    with patch('os.path.exists', return_value=True):
                        with patch('os.remove'):
                            with patch('ir_linker.restore_private_linkage', return_value=restored_ir) as mock_restore:

                                mock_source = MagicMock()
                                mock_func = MagicMock()
                                mock_output = MagicMock()

                                mock_source.name = "/tmp/source.ll"
                                mock_func.name = "/tmp/func.ll"
                                mock_output.name = "/tmp/output.ll"

                                mock_temp.side_effect = [mock_source, mock_func, mock_output]
                                mock_run.return_value = MagicMock(returncode=0)

                                result = ir_linker(source_ir, modified_function_ir, function_name)

                                mock_restore.assert_called_once_with(source_ir, merged_ir)
                                assert result == restored_ir

    def test_file_cleanup_on_exception(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove') as mock_remove:

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]
                        mock_run.side_effect = Exception("Subprocess failed")

                        result = ir_linker(source_ir, modified_function_ir, function_name)

                        assert result is None

                        assert mock_remove.call_count == 3

    def test_nonexistent_file_cleanup(self):

        source_ir = "define i32 @main() { ret i32 0 }"
        modified_function_ir = "define i32 @test() { ret i32 1 }"
        function_name = "test"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            with patch('subprocess.run') as mock_run:
                with patch('os.path.exists', return_value=False):
                    with patch('os.remove') as mock_remove:

                        mock_source = MagicMock()
                        mock_func = MagicMock()
                        mock_output = MagicMock()

                        mock_source.name = "/tmp/source.ll"
                        mock_func.name = "/tmp/func.ll"
                        mock_output.name = "/tmp/output.ll"

                        mock_temp.side_effect = [mock_source, mock_func, mock_output]
                        mock_run.return_value = MagicMock(returncode=1)

                        ir_linker(source_ir, modified_function_ir, function_name)

                        mock_remove.assert_not_called()