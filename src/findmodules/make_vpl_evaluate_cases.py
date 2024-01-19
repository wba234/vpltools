'''
Provides functions for automatically generating vpl_evaluate.cases files
for use with Moodle VPL assignments.
'''
import os.path
import unittest
# import importlib
from typing import List, Tuple, Callable, Dict, Union


def overwrite_file_if_different(file_path, new_contents):
    # Two cases for wrtiting the file:
    # 1. It doesn't exist.
    # 2. It's out of date.
    
    try:
        with open(file_path, 'r') as old_file_object:
            old_file_contents = old_file_object.read()

        if old_file_contents != new_contents:
            raise FileNotFoundError

        print("no changes...", end="")
    except FileNotFoundError:
        with open(file_path, "w") as new_file_object:
            new_file_object.write(new_contents)

    print("done.")


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
        if key.startswith("test") and callable(value):
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
    overwrite_file_if_different(vpl_eval_path, all_test_cases_string)


def make_vpl_evaluate_cases(module_name, module_dict_, include_pylint=True):
    print("Making vpl_evaluate.cases...", end="")

    test_methods = {} # keys are class names, values are lists of test method names
    subclasses_dict = get_unittest_subclasses(module_dict_)
    for key, value in subclasses_dict.items():
        test_methods[key] = get_test_method_names(value)

    make_cases_file(module_name, test_methods, include_pylint)
    print("done.")


CASE_PAIR_ARGS = "args"
CASE_PAIR_IN_FILE = "outfile"

def make_vpl_case_pairs(test_cases: List[Dict[str, Union[Tuple, str]]], 
                        local_path_prefix: str,
                        key_program: Callable,
                        student_extension: str = "_student_results.txt", 
                        key_file_extension: str = "_key_results.txt",
                        file_comparison_program: str = "differ.sh"):
    '''
    Use this function when you want to compare a student output file with a key file.
    test_cases : a list of sets of command line arguments for the program being tested.
                These are used for both the student program and the key program. The format 
                for these is that of a dictionary, with the keys ARGS, and IN_FILE.
                ARGS' value should be a tuple of strings. These should be the first N-2nd
                    command line arguments of key_program, and the expected student program.
                IN_FILE's value should be a string; the name of the file which the program 
                    will read from. This should be the N-1st command line argument of both 
                    student and key progrmams. The Nth command line argument of both key 
                    and student programs should be the name of the output file to write to. 
                    That name is generated automatically by this function.
    local_path_prefix : The result of calling os.path.dirname(os.path.abspath(__file__)) 
                in the scope which calls this function. Or wherever the input files can be
                found, and output files should be written. No, those can't be different.

    '''
    # --- YOU SHOULD NOT HAVE TO CHANGE THIS PART --------------------------------------------
    print("Making vpl_evaluate.cases...", end="")

    new_file_contents = ""
    for argument_dict in test_cases:

        # Combine all command line arguments into a single string
        argument_str = " ".join([str(arg) for arg in argument_dict[CASE_PAIR_ARGS]])

        # Figure out which files we'll write to
        file_base_name = os.path.splitext(os.path.basename(argument_dict[CASE_PAIR_IN_FILE]))[0]
        output_file_basename = f"{argument_str.replace(' ', '_')}_{file_base_name}"
        student_output_file_name = output_file_basename + student_extension
        key_output_file_name = output_file_basename + key_file_extension

        # Remember, the triple quotes provide (mostly) WYSIWYG formatting.
        case_pair_format = f'''Case = Run args {argument_str} {argument_dict[CASE_PAIR_IN_FILE]}
    Program arguments = {argument_str} {argument_dict[CASE_PAIR_IN_FILE]} {student_output_file_name}
    Output = ""
    Grade reduction = 100%

Case = Check args {argument_str} {argument_dict[CASE_PAIR_IN_FILE]}
    Program to run = {file_comparison_program}
    Program arguments = {key_output_file_name} {student_output_file_name}
    Output = "Empty diff. #nonewsisgoodnews"
    Grade reduction = 100%

'''
        new_file_contents += case_pair_format
        # brute_force_knapsack.bfk(
        key_program(
            *argument_dict[CASE_PAIR_ARGS],
            os.path.join(local_path_prefix, argument_dict[CASE_PAIR_IN_FILE]), 
            os.path.join(local_path_prefix, key_output_file_name))

    # end for.
    write_to_file = "vpl_evaluate.cases"
    write_to_file = os.path.join(local_path_prefix, write_to_file)

    overwrite_file_if_different(write_to_file, new_file_contents)


if __name__ == '__main__':
    print("make_evaluate_cases_vpl.py: Are you lost? You look lost.")
