import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'test_framework'))
from test_output_parser import detect_framework, parser, FRAMEWORK_MARKERS


def test_detect_framework():
    test_stdout = "Compiling tests/test-file.el\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "ERT"

    test_stdout = "python3 -m unittest\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "PYTHON-UNITTEST"

    test_stdout = "/usr/bin/ctest --test-dir build\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "CTEST"

    test_stdout = "pytest\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "PYTEST"

    test_stdout = "1..5\nok 1 - Test1\nnot ok 2 - Test2\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "TAP"

    test_stdout = "Making check in src\nmake check-TESTS\nmake all-am\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "AUTOTOOLS"

    test_stdout = "ninja: no work to do.\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) == "NINJA"

    test_stdout = "Some unrelated output\n"
    test_stderr = ""
    assert detect_framework(test_stdout, test_stderr) is None

@pytest.mark.parametrize("stdout,expected_detected,expected_framework", [
    ("python3 -m unittest\nRan 10 tests", 1, "PYTHON-UNITTEST"),
    ("/usr/bin/busted\n[=====] 8 tests from 2 test files ran.", 1, "BUSTED"),
    ("pytest\ncollected 12 items", 1, "PYTEST"),
    ("1..15\nok 1 - first test", 1, "TAP"),
    ("ok 1 - test passed", 1, "TAP"),
    ("not ok 2 - test failed", 1, "TAP"),
])
def test_parser_parametrized(stdout, expected_detected, expected_framework):
    stderr = ""
    result = parser(stdout, stderr)
    assert result[0] == expected_detected
    assert result[1] == expected_framework

@pytest.mark.parametrize("stdout", [
    "tests: 9",
    "Overall 8/10 tests succeeded", 
    "Total: 15 tests",
    "PASS: test_example",
    "Running mytest test",
    "all tests passed",
    "passed 3 tests",
    "Tested: 11"
])
def test_parser_generic_patterns(stdout):
    stderr = ""
    result = parser(stdout, stderr)
    assert result[0] == 1
    assert result[1] is None

def test_parser_no_tests_detected():
    stdout = "Building project"
    stderr = "Compilation successful"
    result = parser(stdout, stderr)
    assert result[0] == 0
    assert result[1] is None

def test_parser_zero_tests_not_detected():
    stdout = "Ran 0 tests"
    stderr = ""
    result = parser(stdout, stderr)
    assert result[0] == 0
    assert result[1] is None