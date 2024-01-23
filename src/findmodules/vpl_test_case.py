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

    CASE_NAME_COMMON_FORMAT = " with args {args_str} {input_file_name}"
    PROGRAM_ARGS_COMMON_FORMAT = " {args_str} {test_case_dict[CASE_PAIR_IN_FILE]} "

    VPL_CASE_PARTS = {
        VPLCaseParts.CASE_NAME : {
            VPLCaseType.OUTPUT_COMPARISON           : "Case = Output" + CASE_NAME_COMMON_FORMAT,
            VPLCaseType.RUN_FOR_FILE_GEN            : "Case = Run" + CASE_NAME_COMMON_FORMAT,
            VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "Case = Check stdout, Generate file" + CASE_NAME_COMMON_FORMAT,
            VPLCaseType.FILE_COMPARISON             : "Case = Generate file" + CASE_NAME_COMMON_FORMAT,
            VPLCaseType.PYTHON_UNITTEST             : "Case = {method_name}",
            VPLCaseType.PYLINT_ANALYSIS             : "Case = PyLiny Style Check",
        },
        VPLCaseParts.PROGRAM_TO_RUN : {
            VPLCaseType.OUTPUT_COMPARISON           : "", # Empty by design, defaults to student program.
            VPLCaseType.RUN_FOR_FILE_GEN            : "", # Empty by design, defaults to student program.
            VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "", # Empty by design, defaults to student program.
            VPLCaseType.FILE_COMPARISON             : "    Program to run = {file_comparison_program}",
            VPLCaseType.PYTHON_UNITTEST             : "    Program to run = /usr/bin/python3",
            VPLCaseType.PYLINT_ANALYSIS             : "    Program to run = /usr/bin/python3",
        },
        VPLCaseParts.PROGRAM_ARGUMENTS : {
            VPLCaseType.OUTPUT_COMPARISON           : "    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT,
            VPLCaseType.RUN_FOR_FILE_GEN            : "    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT + "{student_output_file_name}",
            VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT + "{student_output_file_name}",
            VPLCaseType.FILE_COMPARISON             : "    Program arguments = {key_output_file_name} {student_output_file_name}",
            VPLCaseType.PYTHON_UNITTEST             : "    Program arguments = -m unittest{module_name}.{test_class}.{method_name}",
            VPLCaseType.PYLINT_ANALYSIS             : "    Program arugments = -m pylint {module_name}",
        },
        VPLCaseParts.PROGRAM_OUTPUT : {
            VPLCaseType.OUTPUT_COMPARISON           : "    Output = \"{key_output}\"",
            VPLCaseType.RUN_FOR_FILE_GEN            : "",  # Empty by design, no output expected, but can be tolerated.
            VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "    Output = \"{key_output}\"",
            VPLCaseType.FILE_COMPARISON             : "    Output = \"Empty diff. #nonewsisgoodnews\"",
            VPLCaseType.PYTHON_UNITTEST             : "    Output = /.*OK/i",
            VPLCaseType.PYLINT_ANALYSIS             : "    Output = /.*Your code has been rated at 10.00/10*/i",
        },
        VPLCaseParts.GRADE_REDUCTION : {
            VPLCaseType.OUTPUT_COMPARISON           : "    Grade reduction = 100%",
            VPLCaseType.RUN_FOR_FILE_GEN            : "    Grade reduction = 100%",
            VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP: "    Grade reduction = 100%",
            VPLCaseType.PYTHON_UNITTEST             : "    Grade reduction = 100%",
            VPLCaseType.PYLINT_ANALYSIS             : "    Grade resuction = 0%",
        }
    }
 

    def __init__(self, 
                 case_type: SemanticCaseType, 
                 program_arguments: Tuple = (), 
                 program_input_file: str = "", 
                 program_uses_input: bool = True):

        if program_uses_input and program_arguments == () and program_input_file == "":
            raise ValueError("The program must have some input!")

        self.case_type = case_type
        self.args = program_arguments
        self.infile = program_input_file


    @classmethod
    def make_case_block_of_type(cls, case_type: VPLCaseType) -> str:
        block_text = ""
        for case_part in cls.VPL_CASE_PARTS:
            block_text += cls.VPL_CASE_PARTS[case_part][case_type] + "\n"
        block_text += "\n\n"

        return block_text
    

    def make_case_block(self):
        for case_type in self.CASE_TYPE_FOR_SEMANTIC[self.case_type]:
            # Compile a formattable template for the Case.
            case_block += self.make_case_block_of_type(case_type)

            # Compile all the things that needtobesubstitutedinto the Case template.
            args_str = " ".join([str(arg) for arg in self.args])
            file_base_name = os.path.splitext(os.path.basename(self.infile))[0]
            output_file_basename = f"{args_str.replace(' ', '_')}_{file_base_name}"
            student_output_file_name = output_file_basename + self.student_extension
            key_output_file_name = output_file_basename + self.key_file_extension

            # Skip the expected output generation if it is not needed.
            if case_type in (SemanticCaseType.OUTPUT_CHECK,SemanticCaseType.FILE_AND_OUTPUT_CHECK):
                with patch("sys.stdout", new = StringIO()) as captured_output:
                    self.key_program(*self.args,
                                os.path.join(self.local_path_prefix, self.infile))
                    key_output = captured_output.getvalue()

            # Format the Case block and add it to the string 
            return case_block.format(args_str=args_str,
                                                input_file_name=self.infile,
                                                file_comparison_program="differ.sh",
                                                key_output_file_name=key_output_file_name,
                                                student_output_file_name=student_output_file_name,
                                                key_output=key_output)


class VPLProgramTester:

    def __init__(self, 
                 local_path_prefix: str, 
                 key_program: Callable, 
                 student_extension: str = "_student_results.txt",
                 key_file_extension: str = "_key_results.txt",
                 test_cases: List[VPLTestCase] = []):
        self.local_path_prefix = local_path_prefix
        self.key_program = key_program
        self.student_extension = student_extension
        self.key_file_extension = key_file_extension
        self.test_cases = test_cases


    def make_vpl_evaluate_cases(self):

        case_blocks = ""
        for vpl_test_case in self.test_cases:
            case_blocks += vpl_test_case.make_test_case_block()

        write_to_file = "vpl_evaluate.cases"
        write_to_file = os.path.join(self.local_path_prefix, write_to_file)

        findmodules.overwrite_file_if_different(write_to_file, case_blocks)

