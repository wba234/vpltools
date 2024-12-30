'''
Provides functions for automatically generating vpl_evaluate.cases files
for use with Moodle VPL assignments.
'''
import os.path

__unittest = True

def overwrite_file_if_different(file_path, new_contents, verbose=True) -> bool:
    # Two cases for writing the file:
    # 1. It doesn't exist.
    # 2. It's out of date.
    print("\nMaking vpl_evaluate.cases...", end="")
    did_write_file = False
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


def python3_case_block(test_method_description: tuple) -> str:
    module_name, test_class, method_name = test_method_description
    test_case_format = (f"Case = {method_name}" + "\n"
        f"program to run = /usr/bin/python3"    + "\n"
        f"program arguments = -m unittest {module_name}.{test_class}.{method_name}" + "\n"
        f"expected exit code = 0\n"
        f"output = /.*OK/i"                     + "\n"
        f"grade reduction = 100%"               + "\n"
        "\n")
    return test_case_format


def pylint_case_block(module_name):
    pylint_test_case = (
        f"Case = PyLint Style Check" + "\n"
        f"program to run = /usr/bin/python3" + "\n"
        f"program arguments = -m pylint {module_name}" + "\n"
        f"output = /.*Your code has been rated at 10.00/10*/i" + "\n"
        f"grade reduction = 0%" + "\n"
    )
    return pylint_test_case


def get_vpl_eval_path(module_path):
    return os.path.join(
        module_path if os.path.isdir(module_path) else os.path.dirname(module_path), "vpl_evaluate.cases")


def make_cases_file_from_list(module_path, test_method_list, include_pylint):
    all_test_cases_string = ""

    for test_method_description in test_method_list:
        all_test_cases_string += python3_case_block(test_method_description)

    if include_pylint:
        all_test_cases_string += pylint_case_block(test_method_description)

    vpl_eval_path = get_vpl_eval_path(module_path)
    overwrite_file_if_different(vpl_eval_path, all_test_cases_string)

        
if __name__ == '__main__':
    print("make_evaluate_cases_vpl.py: Are you lost? You look lost.")
