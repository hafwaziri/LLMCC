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
def random_function_selector(functions, random_seed=None):

    if random_seed == None:
        random_seed = 42

    random.seed(random_seed)

    try:
        return random.choice(functions)
    except Exception as e:
        print(f"Random Function Extractor error: {e}")

if __name__ == "__main__":


    functions = []

    random_function = random_function_selector(functions)