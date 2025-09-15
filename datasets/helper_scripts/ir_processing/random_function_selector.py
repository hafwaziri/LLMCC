"""
random_function_selector.py - Select a random function from a list with reproducibility

Description:
    This module provides a utility to select a random function from a given list of functions.
    The selection can be made reproducible by specifying a random seed.

Functions:
    random_function_selector(functions, random_seed=None)
        Selects and returns a random function from the provided list.
        If random_seed is specified, the selection is reproducible.
"""

import random

#TODO: See if its better to select certain functions for IR Processing
def random_function_selector(functions_from_source, functions_from_ir, random_seed=None):

    if random_seed is None:
        random_seed = 42

    random.seed(random_seed)

    try:
        if functions_from_source and functions_from_ir:

            ir_base_to_full = {}

            for ir_func in functions_from_ir:

                base_name = ir_func

                if '(' in base_name:
                    base_name = base_name.split('(')[0]

                if '::' in base_name:
                    base_name = base_name.split('::')[-1]

                if base_name in ir_base_to_full:
                    ir_base_to_full[base_name] = None
                else:
                    ir_base_to_full[base_name] = ir_func

            valid_functions = []
            for source_func in functions_from_source:
                if source_func in ir_base_to_full and ir_base_to_full[source_func] is not None:
                    valid_functions.append((source_func, ir_base_to_full[source_func]))

            if valid_functions:
                return random.choice(valid_functions)

        return None, None
    except Exception as e:
        print(f"Random Function Extractor error: {e}")
        return None, None

if __name__ == "__main__":
    pass

    # functions = []

    # random_function = random_function_selector(functions)
