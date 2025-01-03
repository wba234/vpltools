# basic_tests.py -- William Bailey -- 19 May 2023.
'''
A module for automatic discovery of student submission files in the 
current working directory. Intended for use with Moodle VPL activities.
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

BASIC_TESTS = [
    has_no_globals,
    has_main_function,
]

def run_basic_tests(module, skip_basic_tests):
    for test_function in BASIC_TESTS:
        if test_function in skip_basic_tests:
            continue

        try:
            test_function(module)
        except NameError:
            print(f"Unable to skip unknown test '{test_function}'")
