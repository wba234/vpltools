'''
basic_tests.py -- William Bailey -- william.bailey@centre.edu -- May 2023

A set of checks for adherence to common programming practices, such as:
- prohibitions on the use of "global" (module scope) variable,
- use of a main function. 
These are specifically for Python programs.

To add another basic test, perform the following steps:
1. Define a function which performs the test. The function should return True
   if the test passes, and raise BasicTestFailedError if the test fails.
2. Include the function in the list basic_tests.BASIC_TESTS, at the end of this file.
'''

__unittest = True

DEFAULT_EXTENSION = ".py"

# ----------------------------------------------------------------------------------------

class BasicTestFailedError(RuntimeError):
    pass


KNOWN_BUILT_IN_NAMES = [
    '__name__', 
    '__doc__', 
    '__package__', 
    '__loader__', 
    '__spec__', 
    '__file__', 
    '__cached__', 
    '__builtins__'
]

def has_no_globals(module) -> bool:
    for obj_name, obj_value in module.__dict__.items():
        if obj_name in KNOWN_BUILT_IN_NAMES:
            continue

        if obj_name.startswith("__"):
            print(f"Ignoring suspected global built in name '{obj_name}'.")
            continue

        if callable(obj_value):
            continue
        
        # Not know or suspected built in, and not callable means GLOBAL VARIABLE! >:-(
        raise BasicTestFailedError("Global variables are forbidden in this assignment!"
                                + f"Global object '{obj_name}' of type '{type(obj_value)}' detected!")
    
    return True


def has_main_function(module) -> bool:
    if hasattr(module, "main"):
        return True
    
    raise BasicTestFailedError(f"This assignment requires a main function!")

# ---------------------------------------------------------------------------------------

BASIC_TESTS = [
    has_no_globals,
    has_main_function,
]

def run_basic_tests(module, run_basic_tests):
    for test_function in run_basic_tests:
        try:
            test_function(module)
        except NameError:
            print(f"Unable to skip unknown test '{test_function}'")
