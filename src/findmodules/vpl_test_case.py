import os.path
from enum import Enum
from typing import Tuple, Callable, List
from io import StringIO
from unittest.mock import patch

import findmodules

class SemanticCaseType(Enum):
    '''
    This captures the idea that there are basically three ways in which you can 
    test student programs; by checking the output, checking the output files, or both.

    For a description of this class significance, see VPLCaseType.
    '''
    FILE_CHECK = 1
    OUTPUT_CHECK = 2
    FILE_AND_OUTPUT_CHECK = 3



class VPLCaseType(Enum):
    '''
    When writing the blocks of text to vpl_evaluate.cases which serve as test cases
    as far as VPL is concerned, they come in 4 flavors. These flavors are influenced
    by the implementation of the test. 
    
    If you are comparing the stdout from a student's program to that of a program
    you wrote, this uses an OUTPUT_COMPARISON Case type. The output from your answer 
    key program is included in the "Output" section of the VPL Case block.

    If you are comparing the contents of a file created by the student's program to the
    contents of an answer key file you upload to Moodle as part of a VPL module, this
    uses two Case types: a RUN_FOR_FILE_GEN, and a FILE_COMPARISON. The first of which
    simply runs the student program as usual, but with no requirements on output.
    The second invokes a program which compares two files. Currently, this relies on a
    script (differ.sh) which is just a this wrapper on the classic diff command line tool.

    If you are evaluating a student program's output to both stdout and to a file, then
    RUN_FOR_FILE_GEN_OUTPUT_COMP and FILE_COMPARISON Cases are used. The former is
    similar to RUN_FOR_FILE_GEN, except it has output expectations like OUTPUT_COMPARISON.
    '''
    OUTPUT_COMPARISON = 1
    RUN_FOR_FILE_GEN = 2
    RUN_FOR_FILE_GEN_OUTPUT_COMP = 3
    FILE_COMPARISON = 4
    PYTHON_UNITTEST = 5
    PYLINT_ANALYSIS = 6



class TestCaseInfo(Enum):
    ARGUMENTS = 1
    INPUT_FILE = 2
    CASE_TYPE = 3



class VPLCaseParts(Enum):
    '''
    Thic captures the idea that there are a few necessary components of a VPL Case
    block. They make the most sense to appear in the order shown in the code, but 
    will work as long as CASE_NAME is first.
    '''
    CASE_NAME = 1
    PROGRAM_TO_RUN = 2
    PROGRAM_ARGUMENTS = 3
    PROGRAM_OUTPUT = 4
    GRADE_REDUCTION = 5



class VPLTestCase:

    CASE_TYPE_FOR_SEMANTIC = {
        SemanticCaseType.FILE_CHECK             : (
            VPLCaseType.RUN_FOR_FILE_GEN, 
            VPLCaseType.FILE_COMPARISON,
        ),
        SemanticCaseType.OUTPUT_CHECK           : (
            VPLCaseType.OUTPUT_COMPARISON,
        ),
        SemanticCaseType.FILE_AND_OUTPUT_CHECK  : (
            VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP, 
            VPLCaseType.FILE_COMPARISON,
            )
        }

    CASE_NAME_COMMON_FORMAT = " with args {args_str}"
    
    PROGRAM_ARGS_COMMON_FORMAT = " {args_str} "
    
    # PYLINT_ARGS: List[str] = []
    # PYLINT_ARGS = " ".join(PYLINT_ARGS)

    VPL_CASE_TEMPLATES = {
        VPLCaseType.OUTPUT_COMPARISON           :(
              "Case = Output" + CASE_NAME_COMMON_FORMAT
            + "\n    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT
            + "\n    Output = \"{key_output}\""
            + "\n    Grade reduction = 100%"
            + "\n"
        ),
        VPLCaseType.RUN_FOR_FILE_GEN            :(
              "Case = Run" + CASE_NAME_COMMON_FORMAT
            + "\n    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT
            + "\n    Grade reduction = 100%"
            + "\n"
        ),
        VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP:(
              "Case = Check stdout, Generate file" + CASE_NAME_COMMON_FORMAT
            + "\n    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT
            + "\n    Output = \"{key_output}\""
            + "\n    Grade reduction = 100%"
            + "\n"
        ),
        VPLCaseType.FILE_COMPARISON             :(
              "Case = Check output file" + CASE_NAME_COMMON_FORMAT
            + "\n    Program to run = {file_comparison_program}"
            + "\n    Program arguments = {key_output_file_name} {student_output_file_name}"
            + "\n    Output = \"Empty diff. #nonewsisgoodnews\""
            + "\n    Grade reduction = 100%"
            + "\n"
        ),
        VPLCaseType.PYTHON_UNITTEST             :(
              "Case = {method_name}"
            + "\n    Program to run = /usr/bin/python3"
            + "\n    Program arguments = -m unittest{module_name}.{test_class}.{method_name}"
            + "\n    Output = /.*OK/i"
            + "\n"
        ),
        VPLCaseType.PYLINT_ANALYSIS             :(
              "Case = PyLiny Style Check"
            + "\n    Program to run = /usr/bin/python3"
            + "\n    Program arugments = -m pylint {module_name}" # + " " + PYLINT_ARGS
            + "\n    Output = /.*Your code has been rated at 10.00/10*/i"
            + "\n    Grade reduction = 0%"
            + "\n"
        )
    }
 
    student_extension = "_student_results.txt"
    key_file_extension = "_key_results.txt"


    def __init__(self, 
                 case_type: SemanticCaseType, 
                 key_program: Callable,
                 local_path_prefix: str,
                 program_arguments: Tuple = (),
                 outfile_index: int = None,
                 key_outfile: str = "",
                 program_uses_input: bool = True):

        if program_uses_input and program_arguments == ():
            raise ValueError("The program must have some arguments! Override with program_uses_input=False")

        self.case_type = case_type
        self.key_program = key_program
        self.local_path_prefix = local_path_prefix
        self.args = program_arguments
        self.outfile_index = outfile_index
        self.key_outfile = key_outfile
        self.uses_input = program_uses_input

        self.args_str = " ".join([str(arg) for arg in self.args])


    def __repr__(self):
        return f"VPLTestCase({self.case_type}, program_arguments={self.args}, outfile_index={self.outfile_index}, program_uses_input={self.uses_input}"
    

    def get_output_file_basename(self):
        return f"{self.args_str.replace(' ', '_')}"


    def get_student_output_file_name(self):
        if self.outfile_index is not None:
            return os.path.basename(self.args[self.outfile_index])
            # Do we need the basename() call?

        return self.get_key_output_file_base_name() + self.student_extension
    

    def get_key_output_file_name(self):
            if self.key_outfile == "":
                return self.get_output_file_basename() + self.key_file_extension
        
            return self.key_outfile
    

    def get_key_output(self):
        # Skip the expected output generation if it is not needed.
        key_output = ""
        if self.case_type in (SemanticCaseType.OUTPUT_CHECK,SemanticCaseType.FILE_AND_OUTPUT_CHECK):
            with patch("sys.stdout", new = StringIO()) as captured_output:
                self.key_program(*self.args)#,
                            # os.path.join(self.local_path_prefix, self.infile))
                key_output = captured_output.getvalue()

        return key_output
    

    def make_all_case_blocks(self):
        all_case_blocks = ""
        for case_type in self.CASE_TYPE_FOR_SEMANTIC[self.case_type]:

            # Compile all the things that need to be substituted into the Case template.
            template_placeholder_values = {
                "args_str"                  : self.args_str,
                "student_output_file_name"  : self.get_student_output_file_name(),
                "key_output_file_name"      : self.get_key_output_file_name(),
                "key_output"                : self.get_key_output(),
                "file_comparison_program"   : "differ.sh",
                # vv Python-specific vv
                "method_name"               : "",
                "module_name"               : "",
                "test_class"                : "",
            }

            # Format the Case block and add it to the string 
            case_block = self.VPL_CASE_TEMPLATES[case_type]
            all_case_blocks += case_block.format(**template_placeholder_values) + "\n"

        return all_case_blocks



class VPLProgramTester:

    def __init__(self, 
                 local_path_prefix: str, 
                 test_cases: List[VPLTestCase] = []):
        self.local_path_prefix = local_path_prefix
        self.test_cases = test_cases
        

    def add_test_case(self, test_case):
        self.test_cases.append(test_case)


    def make_vpl_evaluate_cases(self):
        print("Making vpl_evaluate.cases...", end="")
        case_blocks = ""
        for vpl_test_case in self.test_cases:
            case_blocks += vpl_test_case.make_all_case_blocks()

        write_to_file = "vpl_evaluate.cases"
        write_to_file = os.path.join(self.local_path_prefix, write_to_file)

        if not findmodules.overwrite_file_if_different(write_to_file, case_blocks, verbose=False):
            print("no changes...", end="")
        
        print("done.")


if __name__ == "__main__":
    print("Are you lost? You look lost.")
