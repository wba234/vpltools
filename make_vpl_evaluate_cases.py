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
        if key.startswith("test"):
            test_method_names.append(key)

    return test_method_names


def make_cases_file(module_path, test_methods, include_pylint):
    vpl_eval_path = os.path.join(os.path.dirname(module_path), "vpl_evaluate.cases")
    vpl_evaluate_cases_fo = open(vpl_eval_path, "w")
    module_name, extension = os.path.splitext(os.path.basename(module_path))
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
            print(test_case_format, file=vpl_evaluate_cases_fo)
    if include_pylint:
        py_lint_test_case = f'''
Case = PyLint Style Check
program to run = /usr/bin/python3
program arguments = -m pylint {module_name}
output = /.*Your code has been rated at 10.00/10*/i
grade reduction = 0%
'''
        print(py_lint_test_case, file=vpl_evaluate_cases_fo)

    vpl_evaluate_cases_fo.close()


def make_vpl_evaluate_cases(module_name, module_dict_, include_pylint=True):
    print("Making vpl_evaluate.cases...", end="")
    # MODULE = test_formatting_time
    # module_name = MODULE.__name__

    test_methods = {} # keys are class names, values are lists of method names
    #module_object = importlib.import_module(module_name)
    subclasses_dict = get_unittest_subclasses(module_dict_)
    for key, value in subclasses_dict.items():
        test_methods[key] = get_test_method_names(value)

    # print(test_methods)
    make_cases_file(module_name, test_methods, include_pylint)
    print("done.")


if __name__ == '__main__':
    print("make_evaluate_cases_vpl.py: Are you lost? You look lost.")
