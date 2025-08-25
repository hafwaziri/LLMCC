"""
random_function_selector.py - 

Description:


Functions:

"""

import random

#TODO: See if its better to select certain functions for IR Processing
def random_function_selector(functions, random_seed=None):

    if random_seed == None:
        random_seed = 42
    
    random.seed(random_seed)
    
    random_function = random.choice(functions)
    
    return random_function

if __name__ == "__main__":


    functions = []

    random_function = random_function_selector(functions)