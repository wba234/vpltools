# findmodule.py -- William Bailey -- 19 May 2023.
'''
A module for automatic discovery of student submission files in the 
current working directory. Intend for use with Moodle VPL activities.
'''
import importlib
import os.path
import warnings
from make_vpl_evaluate_cases import make_vpl_evaluate_cases

DEFAULT_EXTENSION = ".py"

class BasicTestFailedError(RuntimeError):
    pass

def find_all_modules_in_dir(use_directory=None, remove_tests=True, verbose=False, extension=DEFAULT_EXTENSION):
    '''
    Returns a list of the names of all files in use_directory which end with DEFAULT_EXTENSION.
    If remove_tests is True, those which begin with "test" will be removed from the list.
    If verbose is True, the entire list, removed items, and kept items will be printed.
    '''
    if use_directory is None:
        use_directory = os.path.dirname(__file__)
        warnings.warn(f"No search directory specified, using: {use_directory}", UserWarning)

    python_files = [
        file for file in os.listdir(use_directory)
        if file.endswith(extension) and not (file.lower().startswith("test") and remove_tests)
    ]

    if verbose:
        print(python_files)

    return python_files


def run_basic_tests(module):
    basic_test_messages = [
        (hasattr(module, "main"), "A main() function is required!"),
        # TODO: No global variables!
    ]
    
    for basic_test in basic_test_messages:
        if not basic_test[0]:
            raise BasicTestFailedError(basic_test[1])


def student_module_name(use_directory, ignore_when_testing=[None], module_extension=DEFAULT_EXTENSION, keep_extension=True):

    module_names = find_all_modules_in_dir(use_directory, remove_tests=True, extension=module_extension)

    # If it's a string, put it into a list.
    if isinstance(ignore_when_testing, str):
        ignore_when_testing = [ignore_when_testing]

    # Ignore me.
    this_file_name = os.path.basename(__file__)
    ignore_when_testing.append(this_file_name)
                               
    # Then loop over the list, as if it had been a list the whole time. Because it might have been.
    for ignored_module in ignore_when_testing:
        if ignored_module is None:
            continue
        
        # Add the module extension if it's not already there.
        if not ignored_module.endswith(module_extension):
            ignored_module += module_extension

        # Remove the module, unless it's not there, in which case, warn about it.
        try:
            module_names.remove(ignored_module)
        except ValueError:
            if ignored_module == this_file_name:
                continue # Don't warn. We know.

            warnings.warn(f"Module '{ignored_module}' not found, not ignored.", RuntimeWarning)

    if len(module_names) > 1:
        raise ImportError(f"More than one file found: {module_names}. Exiting...")

    if len(module_names) < 1:
        raise ImportError(f"No other {module_extension} files found! Exiting...")
    
    module_name = module_names[0]
    if not keep_extension:
        module_name = module_name[:-1*len(module_extension)]

    return module_name


def import_student_module(use_directory, ignore_when_testing=[None], module_extension=DEFAULT_EXTENSION, basic_tests=True):
    '''
    Searches the local directory for files ending in module_extension. 
    Ignores module_to_test, and things starting with "test".
    ignore_when_testing can be a string, or a list of strings, with our without the module_extension.
    '''
    module = student_module_name(
        use_directory, 
        ignore_when_testing=ignore_when_testing, 
        module_extension=module_extension,
        keep_extension=False)
    
    imported_module = importlib.import_module(module)

    if basic_tests:
        run_basic_tests(imported_module) # Raises excception on any failures. Deliberately not caught.

    return imported_module


def import_key_module(use_directory, module_extension=DEFAULT_EXTENSION):
    key_files = [
        file for file in os.listdir(use_directory)
        if file.lower().startswith("key_") and file.endswith(module_extension)
    ]
    if len(key_files) != 1:
        raise RuntimeError(f"Couldn't resolve key file! {len(key_files)} files found: {key_files}")

    return key_files[0]


def main():
    print(find_all_modules_in_dir(os.path.dirname(__file__), remove_tests=True))
    # print(find_all_modules(os.path.dirname(__file__), remove_tests=True))
    print(import_student_module(os.path.dirname(__file__), "__init__.py"))


if __name__ == "__main__":
    main()
