'''
Provides functions for automatically generating vpl_evaluate.cases files
for use with Moodle VPL assignments.
'''
import os.path
import unittest
from typing import List, Tuple, Callable, Dict, Union
from unittest.mock import patch
from io import StringIO
from enum import Enum

def overwrite_file_if_different(file_path, new_contents, verbose=True) -> bool:
    # Two cases for wrtiting the file:
    # 1. It doesn't exist.
    # 2. It's out of date.
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

def get_unittest_subclasses(unittest_module_dict) -> dict:
    '''
    Searches globals() for objects which are subclasses of unittest.TestCase.
    Returns a dictionary: ClassName : ClassObject
    '''
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
    # TODO: make this use VPL_CASE_PARTS.

    vpl_eval_path = os.path.join(
        module_path if os.path.isdir(module_path) else os.path.dirname(module_path), 
        "vpl_evaluate.cases")
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


def make_vpl_evaluate_cases(module_name, module_dict, include_pylint=True):
    print("Making vpl_evaluate.cases...", end="")
    # TODO: This malarky is NOT necessary. See findmofules.opaquetest.tearDownClass() 
    # for an example of how to to this more simply.
    test_methods = {} # keys are class names, values are lists of test method names
    subclasses_dict = get_unittest_subclasses(module_dict)
    for key, value in subclasses_dict.items():
        test_methods[key] = get_test_method_names(value)
        # ClassName : [testMethodName, testMethodName, ...]

    make_cases_file(module_name, test_methods, include_pylint)
    print("done.")


CASE_PAIR_ARGS = "args"
CASE_PAIR_IN_FILE = "infile"
CASE_PAIR_TYPE = "semantic_case_type"

def make_vpl_case_pairs(test_cases: List[Dict[str, Union[Tuple, str]]], 
                        local_path_prefix: str,
                        key_program: Callable,
                        student_extension: str = "_student_results.txt", 
                        key_file_extension: str = "_key_results.txt",
                        file_comparison_program: str = "differ.sh",
                        delay_write: bool = False) -> Union[None, str]:
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
        
    if delay_write:
        return new_file_contents

    write_to_file = "vpl_evaluate.cases"
    write_to_file = os.path.join(local_path_prefix, write_to_file)

    overwrite_file_if_different(write_to_file, new_file_contents)


def make_vpl_output_comparison_cases(test_cases: List[Dict[str, Union[Tuple, str]]], 
                                     local_path_prefix: str,
                                     key_program: Callable,
                                     delay_write: bool = False) -> Union[None, str]:
    print("Making vpl_evaluate.cases...", end="", flush=True)
    all_test_cases_string = ""
    for test_case_dict in test_cases:
        args_string = " ".join([str(arg) for arg in test_case_dict[CASE_PAIR_ARGS]])

        with patch("sys.stdout", new = StringIO()) as captured_output:
            key_program(*test_case_dict[CASE_PAIR_ARGS],
                        os.path.join(local_path_prefix, test_case_dict[CASE_PAIR_IN_FILE]))
            key_output = captured_output.getvalue()

        test_case_text = f'''Case = Test args {args_string} {test_case_dict[CASE_PAIR_IN_FILE]}
    Program arguments = {args_string} {test_case_dict[CASE_PAIR_IN_FILE]}
    Output = "{key_output}"
    Grade reduction = 100%

'''
        all_test_cases_string += test_case_text
    # end for

    if delay_write:
        return all_test_cases_string
    
    vpl_evaluate_cases_file = os.path.join(local_path_prefix, "vpl_evaluate.cases")
    overwrite_file_if_different(vpl_evaluate_cases_file, all_test_cases_string)


# def make_vpl_output_and_case_pairs(file_comparison_cases: List[Dict[str, Union[Tuple, str]]], 
#                                    output_comparison_cases: List[Dict[str, Union[Tuple, str]]],
#                                    both_comparison_cases: List[Dict[str, Union[Tuple, str]]],
#                                    local_path_prefix: str,
#                                    key_program: Callable) -> None:
#     print("Making vpl_evaluate_cases...", end="", flush=True)
#     all_test_cases_string = ""
#     all_test_cases_string += make_vpl_output_comparison_cases(output_comparison_cases,
#                                                               local_path_prefix=local_path_prefix,
#                                                               key_program=key_program,
#                                                               delay_write=True)
    
#     all_test_cases_string += make_vpl_case_pairs(file_comparison_cases, 
#                                                  local_path_prefix=local_path_prefix, 
#                                                  key_program=key_program,
#                                                  delay_write=True)
    

#     write_to_file = "vpl_evaluate.cases"
#     write_to_file = os.path.join(local_path_prefix, write_to_file)

#     overwrite_file_if_different(write_to_file, all_test_cases_string)


# class VPLCaseType(Enum):
#     '''
#     When writing the blocks of text to vpl_evaluate.cases which serve as test cases
#     as far as VPL is concerned, they come in 4 flavors. These flavors are influenced
#     by the implementation of the test. 
    
#     If you are comparing the stdout from a student's program to that of a program
#     you wrote, this uses an OUTPUT_COMPARISON Case type. The output from your answer 
#     key program is included in the "Output" section of the VPL Case block.

#     If you are comparing the contents of a file created by the student's program to the
#     contents of an answer key file you upload to Moodle as part of a VPL module, this
#     uses two Case types: a RUN_FOR_FILE_GEN, and a FILE_COMPARISON. The first of which
#     simply runs the student program as usual, but with no requirements on output.
#     The second invokes a program which compares two files. Currently, this relies on a
#     script (differ.sh) which is just a this wrapper on the classic diff command line tool.

#     If you are evaluating a student program's output to both stdout and to a file, then
#     RUN_FOR_FILE_GEN_OUTPUT_COMP and FILE_COMPARISON Cases are used. The former is
#     similar to RUN_FOR_FILE_GEN, except it has output expectations like OUTPUT_COMPARISON.
#     '''
#     OUTPUT_COMPARISON = 1
#     RUN_FOR_FILE_GEN = 2
#     RUN_FOR_FILE_GEN_OUTPUT_COMP = 3
#     FILE_COMPARISON = 4
#     PYTHON_UNITTEST = 5
#     PYLINT_ANALYSIS = 6


# class SemanticCaseType(Enum):
#     '''
#     This captures the idea that there are basically three ways in which you can 
#     test student programs; by checking the output, checking the output files, or both.

#     For a description of this class significance, see VPLCaseType.
#     '''
#     FILE_CHECK = 1
#     OUTPUT_CHECK = 2
#     FILE_AND_OUTPUT_CHECK = 3


# NOTE: Case blocks are generated in the order you see in each tuple.
# FILE_COMPARISON Cases must be second.
# CASE_TYPE_FOR_SEMANTIC = {
#     SemanticCaseType.FILE_CHECK             : (
#         VPLCaseType.RUN_FOR_FILE_GEN, 
#         VPLCaseType.FILE_COMPARISON,
#     ),
#     SemanticCaseType.OUTPUT_CHECK           : (
#         VPLCaseType.OUTPUT_COMPARISON,
#     ),
#     SemanticCaseType.FILE_AND_OUTPUT_CHECK  : (
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP, 
#         VPLCaseType.FILE_COMPARISON,
#         )
# }


# class VPLCaseParts(Enum):
#     '''
#     Thic captures the idea that there are a few necessary components of a VPL Case
#     block. They make the most sense to appear in the order shown in the code, but 
#     will work as long as CASE_NAME is first.
#     '''
#     CASE_NAME = 1
#     PROGRAM_TO_RUN = 2
#     PROGRAM_ARGUMENTS = 3
#     PROGRAM_OUTPUT = 4
#     GRADE_REDUCTION = 5

# CASE_NAME_COMMON_FORMAT = " with args {args_str} {input_file_name}"
# PROGRAM_ARGS_COMMON_FORMAT = " {args_str} {test_case_dict[CASE_PAIR_IN_FILE]} "

# VPL_CASE_PARTS = {
#     VPLCaseParts.CASE_NAME : {
#         VPLCaseType.OUTPUT_COMPARISON           : "Case = Output" + CASE_NAME_COMMON_FORMAT,
#         VPLCaseType.RUN_FOR_FILE_GEN            : "Case = Run" + CASE_NAME_COMMON_FORMAT,
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "Case = Check stdout, Generate file" + CASE_NAME_COMMON_FORMAT,
#         VPLCaseType.FILE_COMPARISON             : "Case = Generate file" + CASE_NAME_COMMON_FORMAT,
#         VPLCaseType.PYTHON_UNITTEST             : "Case = {method_name}",
#         VPLCaseType.PYLINT_ANALYSIS             : "Case = PyLiny Style Check",
#     },
#     VPLCaseParts.PROGRAM_TO_RUN : {
#         VPLCaseType.OUTPUT_COMPARISON           : "", # Empty by design, defaults to student program.
#         VPLCaseType.RUN_FOR_FILE_GEN            : "", # Empty by design, defaults to student program.
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "", # Empty by design, defaults to student program.
#         VPLCaseType.FILE_COMPARISON             : "    Program to run = {file_comparison_program}",
#         VPLCaseType.PYTHON_UNITTEST             : "    Program to run = /usr/bin/python3",
#         VPLCaseType.PYLINT_ANALYSIS             : "    Program to run = /usr/bin/python3",
#     },
#     VPLCaseParts.PROGRAM_ARGUMENTS : {
#         VPLCaseType.OUTPUT_COMPARISON           : "    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT,
#         VPLCaseType.RUN_FOR_FILE_GEN            : "    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT + "{student_output_file_name}",
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT + "{student_output_file_name}",
#         VPLCaseType.FILE_COMPARISON             : "    Program arguments = {key_output_file_name} {student_output_file_name}",
#         VPLCaseType.PYTHON_UNITTEST             : "    Program arguments = -m unittest{module_name}.{test_class}.{method_name}",
#         VPLCaseType.PYLINT_ANALYSIS             : "    Program arugments = -m pylint {module_name}",
#     },
#     VPLCaseParts.PROGRAM_OUTPUT : {
#         VPLCaseType.OUTPUT_COMPARISON           : "    Output = \"{key_output}\"",
#         VPLCaseType.RUN_FOR_FILE_GEN            : "",  # Empty by design, no output expected, but can be tolerated.
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "    Output = \"{key_output}\"",
#         VPLCaseType.FILE_COMPARISON             : "    Output = \"Empty diff. #nonewsisgoodnews\"",
#         VPLCaseType.PYTHON_UNITTEST             : "    Output = /.*OK/i",
#         VPLCaseType.PYLINT_ANALYSIS             : "    Output = /.*Your code has been rated at 10.00/10*/i",
#     },
#     VPLCaseParts.GRADE_REDUCTION : {
#         VPLCaseType.OUTPUT_COMPARISON           : "    Grade reduction = 100%",
#         VPLCaseType.RUN_FOR_FILE_GEN            : "    Grade reduction = 100%",
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "    Grade reduction = 100%",
#         VPLCaseType.PYTHON_UNITTEST             : "    Grade reduction = 100%",
#         VPLCaseType.PYLINT_ANALYSIS             : "    Grade resuction = 0%",
#     }
# }

# CASE_TYPE = "semantic_case_type"

# def make_case_block_of_type(case_type: VPLCaseType):
#     block_text = ""
#     for case_part in VPL_CASE_PARTS:
#         block_text += VPL_CASE_PARTS[case_part][case_type]
#     block_text += "\n"

#     return block_text


# def make_vpl_cases_generator(test_cases: List[Dict[str, Union[Tuple, str, SemanticCaseType]]], 
#                              local_path_prefix: str, 
#                              key_program: Callable,
#                              student_extension: str = "_student_results.txt",
#                              key_file_extension: str = "_key_results.txt") -> None:
#     all_VPL_Cases = ""

#     for test_case in test_cases:
#         case_block = ""
#         for case_type in CASE_TYPE_FOR_SEMANTIC[test_case[CASE_TYPE]]:
#             # Compile a formattable template for the Case.
#             case_block += make_case_block_of_type(case_type)

#             # Compile all the things that needtobesubstitutedinto the Case template.
#             args_str = " ".join([str(arg) for arg in test_case[CASE_PAIR_ARGS]])
#             file_base_name = os.path.splitext(os.path.basename(test_case[CASE_PAIR_IN_FILE]))[0]
#             output_file_basename = f"{args_str.replace(' ', '_')}_{file_base_name}"
#             student_output_file_name = output_file_basename + student_extension
#             key_output_file_name = output_file_basename + key_file_extension

#             # Skip the expected output generation if it is not needed.
#             if case_type in (SemanticCaseType.OUTPUT_CHECK,SemanticCaseType.FILE_AND_OUTPUT_CHECK):
#                 with patch("sys.stdout", new = StringIO()) as captured_output:
#                     key_program(*test_case[CASE_PAIR_ARGS],
#                                os.path.join(local_path_prefix, test_case[CASE_PAIR_IN_FILE]))
#                     key_output = captured_output.getvalue()

#             # Format the Case block and add it to the string 
#             all_VPL_Cases += case_block.format(args_str=args_str,
#                                                input_file_name=test_case[CASE_PAIR_IN_FILE],
#                                                file_comparison_program="differ.sh",
#                                                key_output_file_name=key_output_file_name,
#                                                student_output_file_name=student_output_file_name,
#                                                key_output=key_output)

#     write_to_file = "vpl_evaluate.cases"
#     write_to_file = os.path.join(local_path_prefix, write_to_file)

#     overwrite_file_if_different(write_to_file, all_VPL_Cases)

        
if __name__ == '__main__':
    print("make_evaluate_cases_vpl.py: Are you lost? You look lost.")
