import os.path
import unittest
import importlib

def get_unittest_subclasses(unittest_module_dict) -> dict:
    unittest_subclasses = {}
    # for key, value in unittest_module.__dict__.items():
    for key, value in unittest_module_dict.items():
        try:
            if issubclass(value, unittest.TestCase):
                unittest_subclasses[key] = value
        except TypeError:
            pass # Needs to be a class.
    
    return unittest_subclasses

def get_test_method_names(unittest_subclass):
    test_method_names = []
    for key, value in unittest_subclass.__dict__.items():
        if key.startswith("test"): # and callable(key):
            test_method_names.append(key)

    return test_method_names


def make_cases_file(module_path, test_methods, include_pylint):
    vpl_eval_path = os.path.join(os.path.dirname(module_path), "vpl_evaluate.cases")
    # vpl_evaluate_cases_fo = open(vpl_eval_path, "w")
    module_name, extension = os.path.splitext(os.path.basename(module_path))

    all_test_cases_string = ""

    for test_class, test_class_methods in test_methods.items():
        for method_name in test_class_methods:
            # command_string = f"python3.9 -m unittest {module_name}.{test_class}.{method_name}"
            # print(command_string)

            test_case_format = f'''
Case = {method_name}
program to run = /usr/bin/python3
program arguments = -m unittest {module_name}.{test_class}.{method_name}
output = /.*OK/i
grade reduction = 100%
'''
            all_test_cases_string += test_case_format + "\n"

    # end for

    if include_pylint:
        py_lint_test_case = f'''
Case = PyLint Style Check
program to run = /usr/bin/python3
program arguments = -m pylint {module_name}
output = /.*Your code has been rated at 10.00/10*/i
grade reduction = 0%
'''
        all_test_cases_string += py_lint_test_case + "\n"
    # end if
    
    try:
        # Two reasons we might want to write the file:
        # 1. There is no file.
        with open(vpl_eval_path, "r") as vpl_evaluate_cases_fo:
            old_test_cases_string = vpl_evaluate_cases_fo.read()

        # 2. The file content needs to be updated.
        if old_test_cases_string != all_test_cases_string:
            raise FileNotFoundError

        print("no changes...", end="")

    except FileNotFoundError:

        with open(vpl_eval_path, "w") as vpl_evaluate_cases_fo:
            vpl_evaluate_cases_fo.write(all_test_cases_string)


def make_vpl_evaluate_cases(module_name, module_dict_, include_pylint=True):
    print("Making vpl_evaluate.cases...", end="")

    test_methods = {} # keys are class names, values are lists of test method names
    subclasses_dict = get_unittest_subclasses(module_dict_)
    for key, value in subclasses_dict.items():
        test_methods[key] = get_test_method_names(value)

    make_cases_file(module_name, test_methods, include_pylint)
    print("done.")


if __name__ == '__main__':
    print("make_evaluate_cases_vpl.py: Are you lost? You look lost.")
