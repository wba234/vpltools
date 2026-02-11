'''
Provides functions for automatically generating vpl_evaluate.cases files
for use with Moodle VPL assignments.
'''
# import os.path
import os

__unittest = True

def overwrite_file_if_different(file_path: str, new_contents: str, verbose: bool = False) -> bool:
    '''
    Given the path to the existing vpl_evaluate.cases file, and 
    the desired contents of the file, update it if they are different.
    '''
    did_write_file = False
    # Two cases for writing the file:
    # 1. It doesn't exist.
    # 2. It's out of date.
    print("\nMaking vpl_evaluate.cases...", end="")
    try:
        with open(file_path, 'r') as old_file_object:
            old_file_contents = old_file_object.read()

        if old_file_contents != new_contents:
            raise FileNotFoundError
        
        if verbose:
            print("no changes...", end="")

    except FileNotFoundError:
        with open(file_path, "w") as new_file_object:
            new_file_object.write(new_contents)
        
        did_write_file = True
    
    if verbose:
        print("done.")

    return did_write_file


def python3_case_block(test_method_description: tuple[str, str, str]) -> str:
    '''
    Returns a string suitable to write to a vpl_evaluate.cases file
    to invoke a single test method from a VPLTestCase.
    Accepts a tuple containing the names of the 
    - test_module, 
    - test_class, and 
    - test_method,
    in that order.

    NOTE: test_module should consist ONLY of a single directory. 
    Multiple nested directories must not be used when publishing to VPL. 
    
    For instance: Suppose your directory structure looks like this:
    my_cs_class/
     |- __init__.py
     |- Labs/
     |   |- __init__.py
     |   |- Lab1/
     |   |   |- __init__.py
     |   |   |- test_lab1.py
     |   |   └- lab1_key.py
     |   └- Lab2/
     |       |- __init__.py
     |       |- test_lab2.py
     |       └- lab2_key.py
     └- Notes/
         |- notes.tex
         └- notes.pdf
    
    The __init__.py files are present at each level so that each directory becomes an importable 
    Python module, enabling unittest to find and run all test automatically. However, this means 
    that test_module will have a different value when test modules are run this way, than it would
    have when tests modules are run singly. In the former, the entire path is included:

    Labs.Lab06_SQL_Queries_1.01_all_owners.test_all_owners.TestOwnerNames.testSelectAllOwners
    
    and in the latter, only the directory directly containing the individual test method is included:

    test_all_owners.TestOwnerNames.testSelectAllOwners

    We make the assumption that the lowest subdirectories in a hierarchy are each meant to become
    a VPL module on Moodle. For this reason, we strip all but the last submodule name, so that test 
    methods are referred to by a name which will let VPL find them, instead of using the extra 
    prefixes which will not be available to VPL at runtime.
    '''
    module_name, test_class, method_name = test_method_description
    module_name = module_name.split(".")[-1]
    test_case_format = (f"Case = {method_name}" + "\n"
        f"program to run = /usr/bin/python3"    + "\n"
        f"program arguments = -m unittest {module_name}.{test_class}.{method_name}" + "\n"
        f"expected exit code = 0\n"
        f"output = /.*OK.*/i"                   + "\n"
        f"grade reduction = 100%"               + "\n"
        "\n")
    return test_case_format


def pylint_case_block(module_name: str) -> str:
    '''
    Returns a string suitable to write to a vpl_evaluate.cases file
    to invoke pylint on the student's submission.
    '''
    pylint_test_case = (
        f"Case = PyLint Style Check" + "\n"
        f"program to run = /usr/bin/python3" + "\n"
        f"program arguments = -m pylint {module_name}" + "\n"
        f"output = /.*Your code has been rated at 10.00/10*/i" + "\n"
        f"grade reduction = 0%" + "\n"
    )
    return pylint_test_case


def get_vpl_eval_path(module_path: str) -> str:
    '''
    Returns the absolute path where vpl_evaluate.cases should be written
    (the same location as the student's module, and test module).
    '''
    return os.path.join(
        module_path 
            if os.path.isdir(module_path) 
            else os.path.dirname(module_path), 
        "vpl_evaluate.cases")


def make_cases_file_from_list(module_path: str, test_method_list: list[tuple[str, str, str]], include_pylint: bool, verbose: bool):
    '''
    Writes or overwrites the vpl_evaluate.cases file located alongside 
    student's module. Writes one "case" block for each element of test_method_list, 
    and another for pylint, if the flag has been set.
    '''
    all_test_cases_string = ""

    for test_method_description in test_method_list:
        all_test_cases_string += python3_case_block(test_method_description)

    if include_pylint and test_method_list:
        all_test_cases_string += pylint_case_block(test_method_list[0][0])

    vpl_eval_path = get_vpl_eval_path(module_path)
    overwrite_file_if_different(vpl_eval_path, all_test_cases_string, verbose)

        
if __name__ == '__main__':
    print("make_evaluate_cases_vpl.py: Are you lost? You look lost.")
