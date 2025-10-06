import os
import sys
import pytest
from unittest.mock import Mock, patch, mock_open
import orjson
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datasets.helper_scripts.package_builder.main import process_package

class TestProcessPackage:

    @pytest.fixture
    def mock_dirs(self):

        package_dir = Mock()
        package_dir.path = "/test/package"
        sub_dir = Mock()
        sub_dir.path = "/test/subdir"
        return package_dir, sub_dir

    @pytest.fixture
    def sample_compilation_data(self):

        return [{
            'source_file': 'test.c',
            'compiler_flags': ['gcc', '-O2'],
            'output_file': 'test.o',
            'source_functions': ['main'],
            'ir_functions': ['main'],
            'random_function': 'main',
            'random_function_mangled': '_main',
            'ir_generation_return_code': 0,
            'llvm_ir': 'define i32 @main()',
            'ir_generation_stderr': '',
            'random_func_ir_generation_return_code': 0,
            'random_func_llvm_ir': 'define i32 @main()',
            'random_func_ir_generation_stderr': '',
            'object_file_generation_return_code': 0,
            'timestamp_check': True,
            'relinked_llvm_ir': 'define i32 @main()',
            'modified_object_file_generation_return_code': 0,
            'modified_object_file_timestamp_check': True
        }]

    @pytest.fixture
    def sample_docker_output(self, sample_compilation_data):

        return orjson.dumps([
            "cmake",  # build_system
            "configure output",  # dh_auto_config
            "build output",  # dh_auto_build
            "test output",  # dh_auto_test
            "build stderr",  # build_stderr
            0,  # build_returncode
            "test stdout",  # test_stdout
            "test stderr",  # test_stderr
            0,  # test_returncode
            True,  # test_detected
            "pytest",  # testing_framework
            "stdout diff",  # test_stdout_diff
            "stderr diff",  # test_stderr_diff
            True,  # package_viable_for_test_dataset
            "rebuild stderr",  # rebuild_stderr
            0,  # rebuild_returncode
            "modified rebuild stderr",  # modified_rebuild_stderr
            0,  # modified_rebuild_returncode
            "test stdout modified",  # test_stdout_for_modified_package
            "test stderr modified",  # test_stderr_for_modified_package
            True,  # test_passed
            sample_compilation_data  # compilation_data
        ]).decode()

    @patch('datasets.helper_scripts.package_builder.main.subprocess.run')
    @patch('datasets.helper_scripts.package_builder.main.os.makedirs')
    def test_successful_processing(self, mock_makedirs, mock_subprocess, mock_dirs, sample_docker_output):

        package_dir, sub_dir = mock_dirs

        mock_result = Mock()
        mock_result.stdout = sample_docker_output
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.open', mock_open()) as mock_file:
                result = process_package(package_dir, sub_dir, temp_dir)

                assert result is True
                mock_subprocess.assert_called_once()
                mock_makedirs.assert_called_once()
                mock_file.assert_called_once()

    @patch('datasets.helper_scripts.package_builder.main.subprocess.run')
    def test_json_decode_error(self, mock_subprocess, mock_dirs):

        package_dir, sub_dir = mock_dirs

        mock_result = Mock()
        mock_result.stdout = "invalid json"
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_package(package_dir, sub_dir, temp_dir)

            assert result is False

    @patch('datasets.helper_scripts.package_builder.main.subprocess.run')
    @patch('datasets.helper_scripts.package_builder.main.os.makedirs')
    def test_output_file_creation(self, mock_makedirs, mock_subprocess, mock_dirs, sample_docker_output):

        package_dir, sub_dir = mock_dirs

        mock_result = Mock()
        mock_result.stdout = sample_docker_output
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.open', mock_open()) as mock_file:
                process_package(package_dir, sub_dir, temp_dir)

                expected_path = os.path.join(temp_dir, "package.json")
                mock_file.assert_called_with(expected_path, 'wb')

    @patch('datasets.helper_scripts.package_builder.main.subprocess.run')
    def test_empty_compilation_data(self, mock_subprocess, mock_dirs):

        package_dir, sub_dir = mock_dirs

        empty_output = orjson.dumps([
            "cmake", "config", "build", "test", "stderr", 0,
            "stdout", "stderr", 0, True, "pytest",
            "diff1", "diff2", True, "rebuild", 0,
            "modified", 0, "test_out", "test_err", True,
            []
        ]).decode()

        mock_result = Mock()
        mock_result.stdout = empty_output
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.open', mock_open()):
                result = process_package(package_dir, sub_dir, temp_dir)

                assert result is True

    @patch('datasets.helper_scripts.package_builder.main.subprocess.run')
    def test_malformed_docker_output(self, mock_subprocess, mock_dirs):
        """Test handling of malformed Docker output structure."""
        package_dir, sub_dir = mock_dirs

        malformed_output = orjson.dumps(["cmake", "config"]).decode()

        mock_result = Mock()
        mock_result.stdout = malformed_output
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_package(package_dir, sub_dir, temp_dir)

            assert result is False