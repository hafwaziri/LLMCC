import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import subprocess


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'test_framework'))

from debian_package_tester import test_package as run_test_package, run_dh_auto_test_command, clean_test_output, handle_test_rerun_and_diff

class TestCleanTestOutput:
    def test_clean_test_output_removes_timing_patterns(self):
        test_input = "Test passed in 123ms and took 45.67 sec to complete"
        result = clean_test_output(test_input)
        assert "123ms" not in result
        assert "45.67 sec" not in result

    def test_clean_test_output_removes_timestamps(self):
        test_input = "Mon Jan 01 12:34:56 2024 - test completed"
        result = clean_test_output(test_input)
        assert "Mon Jan 01 12:34:56 2024" not in result

    def test_clean_test_output_empty_string(self):
        result = clean_test_output("")
        assert result == ""

    def test_clean_test_output_removes_wallclock_secs(self):
        test_input = "Test completed in 42 wallclock secs (user: 30.5, sys: 10.2)"
        result = clean_test_output(test_input)
        assert "42 wallclock secs (user: 30.5, sys: 10.2)" not in result

    def test_clean_test_output_removes_milliseconds(self):
        test_input = "Operation took 250 milliseconds to finish"
        result = clean_test_output(test_input)
        assert "250 milliseconds" not in result

    def test_clean_test_output_removes_load_average(self):
        test_input = "total load average: 1.5, 2.3, 1.8'"
        result = clean_test_output(test_input)
        assert "total load average: 1.5, 2.3, 1.8'" not in result

    def test_clean_test_output_preserves_other_content(self):
        test_input = "This is important content that should remain"
        result = clean_test_output(test_input)
        assert result == test_input

class TestRunDhAutoTestCommand:
    @patch('subprocess.run')
    def test_run_dh_auto_test_command_with_mock(self, mock_run, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "mock output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = run_dh_auto_test_command("echo test", mock_package_subdir)

        assert result.returncode == 0
        assert result.stdout == "mock output"
        mock_run.assert_called_once_with(
            "echo test",
            cwd=tmp_path,
            shell=True,
            timeout=1200,
            capture_output=True,
            text=True
        )

class TestHandleTestRerunAndDiff:
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_different_return_codes(self, mock_run, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_rerun_result = MagicMock()
        mock_rerun_result.returncode = 1
        mock_run.return_value = mock_rerun_result

        stdout_diff, stderr_diff, viable = handle_test_rerun_and_diff(
            "original stdout", "original stderr", "test command", 
            mock_package_subdir, "test_package", 0
        )
        assert stdout_diff == ""
        assert stderr_diff == ""
        assert viable == 0

    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_same_output_same_returncode(self, mock_run, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_rerun_result = MagicMock()
        mock_rerun_result.returncode = 0
        mock_rerun_result.stdout = "test output"
        mock_rerun_result.stderr = "test error"
        mock_run.return_value = mock_rerun_result

        stdout_diff, stderr_diff, viable = handle_test_rerun_and_diff(
            "test output", "test error", "test command", 
            mock_package_subdir, "test_package", 0
        )

        assert stdout_diff == ""
        assert stderr_diff == ""
        assert viable == 1

    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_different_output_same_returncode(self, mock_run, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_rerun_result = MagicMock()
        mock_rerun_result.returncode = 0
        mock_rerun_result.stdout = "modified output"
        mock_rerun_result.stderr = "modified error"
        mock_run.return_value = mock_rerun_result

        stdout_diff, stderr_diff, viable = handle_test_rerun_and_diff(
            "original output", "original error", "test command", 
            mock_package_subdir, "test_package", 0
        )

        assert stdout_diff != ""
        assert stderr_diff != ""
        assert viable == 0
        assert "original_stdout" in stdout_diff
        assert "modified_stdout" in stdout_diff
        assert "original_stderr" in stderr_diff
        assert "modified_stderr" in stderr_diff

    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_timing_differences_ignored(self, mock_run, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_rerun_result = MagicMock()
        mock_rerun_result.returncode = 0
        mock_rerun_result.stdout = "Test completed in 456ms"
        mock_rerun_result.stderr = ""
        mock_run.return_value = mock_rerun_result

        stdout_diff, stderr_diff, viable = handle_test_rerun_and_diff(
            "Test completed in 123ms", "", "test command", 
            mock_package_subdir, "test_package", 0
        )

        assert stdout_diff == ""
        assert stderr_diff == ""
        assert viable == 1

class TestTestPackage:
    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_empty_command_after_rm_removal(self, mock_run, mock_parser, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        result = run_test_package("test_pkg", "\trm temp_file", "autotools", mock_package_subdir)

        assert "Test Command is empty after removing 'rm' directive" in result[1]
        assert result[2] == 3  # returncode
        assert result[3] == 0  # test_detected
        assert result[7] == 0  # package_viable

    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_command_with_rm_directive(self, mock_run, mock_parser, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        mock_parser.parser.return_value = (1, "PYTEST")

        run_test_package("test_pkg", "pytest\trm temp_file", "autotools", mock_package_subdir)

        mock_run.assert_called_with("pytest", mock_package_subdir)

    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_returncode_3_early_exit(self, mock_run, mock_parser, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_result = MagicMock()
        mock_result.returncode = 3
        mock_result.stdout = "test output"
        mock_result.stderr = "test error"
        mock_run.return_value = mock_result

        result = run_test_package("test_pkg", "pytest", "autotools", mock_package_subdir)

        assert result[0] == "test output"  # stdout
        assert result[1] == "test error"   # stderr
        assert result[2] == 3              # returncode
        assert result[3] == 0              # test_detected (not called parser)
        assert result[4] == ""             # framework (empty)
        assert result[5] == ""             # stdout_diff (empty)
        assert result[6] == ""             # stderr_diff (empty)
        assert result[7] == 0              # package_viable

    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_no_tests_detected_early_exit(self, mock_run, mock_parser, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "build output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        mock_parser.parser.return_value = (0, None)

        result = run_test_package("test_pkg", "make", "autotools", mock_package_subdir)

        assert result[2] == 0  # returncode
        assert result[3] == 0  # test_detected
        assert result[4] is None  # framework
        assert result[5] == ""  # stdout_diff (empty)
        assert result[6] == ""  # stderr_diff (empty)
        assert result[7] == 0   # package_viable

    @patch('debian_package_tester.handle_test_rerun_and_diff')
    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_successful_test_flow(self, mock_run, mock_parser, mock_handle_rerun, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_result.stderr = "test error"
        mock_run.return_value = mock_result
        mock_parser.parser.return_value = (1, "PYTEST")
        mock_handle_rerun.return_value = ("", "", 1)

        result = run_test_package("test_pkg", "pytest", "autotools", mock_package_subdir)

        assert result[0] == "test output"    # stdout
        assert result[1] == "test error"     # stderr
        assert result[2] == 0                # returncode
        assert result[3] == 1                # test_detected
        assert result[4] == "PYTEST"         # framework
        assert result[5] == ""               # stdout_diff
        assert result[6] == ""               # stderr_diff
        assert result[7] == 1                # package_viable

        mock_handle_rerun.assert_called_once_with(
            "test output", "test error", "pytest", 
            mock_package_subdir, "test_pkg", 0
        )

    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_exception_handling(self, mock_run, mock_parser, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_run.side_effect = Exception("Subprocess failed")

        result = run_test_package("test_pkg", "pytest", "autotools", mock_package_subdir)

        assert result[0] == ""  # stdout (empty)
        assert "Test_Exception: Subprocess failed" in result[1]  # stderr
        assert result[2] == 3   # returncode
        assert result[3] == 0   # test_detected
        assert result[4] == ""  # framework
        assert result[5] == ""  # stdout_diff
        assert result[6] == ""  # stderr_diff
        assert result[7] == 0   # package_viable

    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_empty_command_string(self, mock_run, mock_parser, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        result = run_test_package("test_pkg", "", "autotools", mock_package_subdir)

        assert "Test Command is empty after removing 'rm' directive" in result[1]
        assert result[2] == 3
        assert result[3] == 0
        assert result[7] == 0

    @pytest.mark.parametrize("command,expected_cleaned", [
        ("pytest\trm temp.txt", "pytest"),
        ("make test\trm *.log", "make test"),
        ("python -m unittest\trm __pycache__", "python -m unittest"),
        ("pytest", "pytest"),
    ])
    @patch('debian_package_tester.test_output_parser')
    @patch('debian_package_tester.run_dh_auto_test_command')
    def test_rm_directive_cleaning_parametrized(self, mock_run, mock_parser, command, expected_cleaned, tmp_path):
        mock_package_subdir = MagicMock()
        mock_package_subdir.path = tmp_path

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        mock_parser.parser.return_value = (1, "TEST")

        run_test_package("test_pkg", command, "autotools", mock_package_subdir)

        if expected_cleaned:
            mock_run.assert_called_with(expected_cleaned, mock_package_subdir)