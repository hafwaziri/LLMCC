import re

#TODO: Check the Regex and provide comments for the patterns

FRAMEWORK_MARKERS = {
    "CTEST": [
        r"/usr/bin/ctest"
    ],
    "ERT": [
        r"Compiling\s+.*tests.*\.el"
    ],
    "PYTHON-UNITTEST": [ #NOT SURE ABOUT THIS ONE
        r"python3?\s+-m\s+unittest",
    ],
    "BUSTED": [
        r"/usr/bin/busted"
    ],
    "PYTEST": [
        r"pytest"
    ],
    "TAP": [
        r"1\.\.\d+",
        r"^ok\s+\d+",
        r"^not ok\s+\d+"
    ],
    "AUTOTOOLS": [
        r"Making\s+check\s+in\s+\S+",
        r"make\s+check-TESTS",
        r"make\s+all-am"
    ],
    "NINJA": [
        r"ninja:\s+no\s+work\s+to\s+do"
    ]
}

def detect_framework(test_stdout, test_stderr):
    combined_output = test_stdout + test_stderr
    
    for framework, patterns in FRAMEWORK_MARKERS.items():
        for pattern in patterns:
            if re.search(pattern, combined_output, re.IGNORECASE):
                return framework
    
    return None

def parser(test_stdout, test_stderr):
    
    test_detected = 0
    framework = None

    
    framework = detect_framework(test_stdout, test_stderr)

    if test_stderr.strip() == "No tests were found!!!":
        return 0
    
    if framework == "CTEST":
        pattern = r"\d+%\s+tests\s+passed,\s+\d+\s+tests\s+failed\s+out\s+of\s+(?:[1-9]\d*)"
        if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE):
            test_detected = 1

    elif framework == "ERT":
        patterns = [
            r"Running\s+(?:[1-9]\d*)\s+tests",
            r"Ran\s+(?:[1-9]\d*)\s+tests"
        ]
        for pattern in patterns:
            if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE):
                test_detected = 1
                break
        
    elif framework == "PYTHON-UNITTEST": #NOT SURE ABOUT THIS ONE
        pattern = r"Ran\s+(?:[1-9]\d*)\s+tests"
        if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE):
            test_detected = 1
            
    elif framework == "BUSTED":
        pattern = r"\[=+\]\s*(?:[1-9]\d*)\s*tests\s+from\s+\d+\s+test\s+files?\s+ran\."
        if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE):
            test_detected = 1
    
    elif framework == "PYTEST":
        pattern = r"collected\s+(?:[1-9]\d*)\s+items"
        if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE):
            test_detected = 1
    
    elif framework == "TAP":
        patterns = [
            r"1\.\.(?:[1-9]\d*)",
            r"^ok\s+(?:[1-9]\d*)",
            r"^not ok\s+(?:[1-9]\d*)"
        ]
        for pattern in patterns:
            if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE | re.MULTILINE):
                test_detected = 1
                break

    elif framework == "AUTOTOOLS":
        patterns = [
            r"Testsuite\s+summary\s+for.*?#\s*TOTAL:\s*(?:[1-9]\d*)",
            r"(?:[1-9]\d*)\s+tests?\s+passed"
        ]
        for pattern in patterns:
            if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE | re.DOTALL):
                test_detected = 1
                break
    
    elif framework == "NINJA":
        pattern = r"Ok:\s*(?:[1-9]\d*)"
        if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE):
            test_detected = 1
        
    
    else:
        patterns = [
            r"tests:\s*(?:[1-9]\d*)",
            r"Overall\s+(?:[1-9]\d*)/(?:[1-9]\d*)\s+tests\s+succeeded",
            r"Total:\s*(?:[1-9]\d*)\s+tests",
            r"PASS:\s+\S+(?<!\.h)(?<!\.c)(?<!\.cpp)(?<!\.cxx)(?<!\.hpp)(?<!\.cc)", #Must make sure that passed tests were not static analysis checks, #TODO must be refined and checked
            r"Running\s+\S+\s+test\b",
            r"all\s+tests\s+passed",
            r"running\s+test\d+",
            r"testing\s+\S+", #TODO: too general, should be either removed or watch out for correctness
            r"[^\w]*passed[^\w]*(?:[1-9]\d*)[^\w]*tests[^\w]*",
            r"Tested:\s*(?:[1-9]\d*)"
        ]
        for pattern in patterns:
            if re.search(pattern, test_stdout + test_stderr, re.IGNORECASE | re.MULTILINE):
                test_detected = 1
                break
    
    return test_detected, framework
    

if __name__ == "__main__":
    
    test_stdout = r"""

    """
    test_stderr = r"""

    """
    
    test_detected = 0
    
    test_detected, framework = parser(test_stdout, test_stderr)
    
    print(test_detected)