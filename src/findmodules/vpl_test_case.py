import subprocess
import warnings
import os.path
from enum import Enum
from typing import Tuple, Callable, List
from io import StringIO
import abc
# from unittest.mock import patch
# from unittest import TestCase
import unittest
import sys
from dataclasses import dataclass
import findmodules

__unittest = True

# class SemanticCaseType(Enum):
#     '''
#     This captures the idea that there are basically three ways in which you can 
#     test student programs; by checking the output, checking the output files, or both.

#     For a description of this class significance, see VPLCaseType.
#     '''
#     FILE_CHECK = 1
#     OUTPUT_CHECK = 2
#     FILE_AND_OUTPUT_CHECK = 3



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



# class TestCaseInfo(Enum):
#     ARGUMENTS = 1
#     INPUT_FILE = 2
#     CASE_TYPE = 3



# class VPLCaseParts(Enum):
#     '''
#     This captures the idea that there are a few necessary components of a VPL Case
#     block. They make the most sense to appear in the order shown in the code, but 
#     will work as long as CASE_NAME is first.
#     '''
#     CASE_NAME = 1
#     PROGRAM_TO_RUN = 2
#     PROGRAM_ARGUMENTS = 3
#     PROGRAM_OUTPUT = 4
#     GRADE_REDUCTION = 5

@dataclass
class SupportedLanguage(abc.ABC):
    name: str
    extension: str

    def __hash__(self):
        '''
        Provided to that this can be used as the key in a dictionary.
        '''
        return hash(self.name)


@dataclass
class SupportedLanguageProgram(abc.ABC):
    '''
    Represents a program written in one of the languages supported by this package.
    This is an abstract base class, which is not instantiated directly. It is intended
    to be extended into another class for each supported language.
    '''
    language: SupportedLanguage
    compilation_commands: list[str]
    main_file_base_name: str
    executable_name: str
    source_files: list[str] = None
    output_file_name: str = None


    @abc.abstractmethod
    def compilationCommand(self):
        '''
        Abstract method to ensure individual languages implement their respective 
        compilation commands. These should raise RunTimeError if compilation fails.
        '''
        raise NotImplementedError


    def compile(self, use_dir):
        # use_cwd = os.path.dirname(os.path.dirname(sys.modules[self.__module__].__file__))
        command = self.compilationCommand()
        # Try the supplied compilation command
        compilation_process: subprocess.CompletedProcess = subprocess.run(
            command,
            cwd=use_dir
        )
        # If that fails, try make
        if compilation_process.returncode:
            compilation_process = subprocess.run(
                ["make"],
                cwd=use_dir
            )
        # If that fails, give up.
        if compilation_process.returncode:
            raise RuntimeError(
                f"Compilation failed!\n"
                + f"command={command}\n"
                + f"stdout={compilation_process.stdout}\n"
                + f"stderr={compilation_process.stderr}\n"
            )
        

class CProgram(SupportedLanguageProgram):
    '''
    Represents a program written in C, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["C"], [ "gcc", "-lm", "-o"], "main", executable_name, source_files, output_file_name)

    def compilationCommand(self):
        return self.compilation_commands + [self.executable_name] + self.source_files
    

class CPPProgram(SupportedLanguageProgram):
    '''
    Represents a program written in C++, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["CPP"], [ "g++", "-lm", "-o"], "main", executable_name, source_files, output_file_name)

    def compilationCommand(self):
        return self.compilation_commands + [self.executable_name] + self.source_files
    

class JavaProgram(SupportedLanguageProgram):
    '''
    Represents a program written in Java, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["JAVA"], ["java"], "main", executable_name, source_files, output_file_name)
    
    def compilationCommand(self):
        return self.compilation_commands + self.source_files


SUPPORTED_LANGUAGES = {
    "C"     : SupportedLanguage("C", ".c"),
    "CPP"   : SupportedLanguage("C++", ".cpp"),
    "JAVA"  : SupportedLanguage("Java", ".java"),
}

OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE = {
    SUPPORTED_LANGUAGES["C"]    :   CProgram,
    SUPPORTED_LANGUAGES["CPP"]  :   CPPProgram,
    SUPPORTED_LANGUAGES["JAVA"] :   JavaProgram,
}

class VPLTestCase(unittest.TestCase):

    VPL_SYSTEM_FILES = [ 
        "vpl_test",
        ".vpl_tester",
        "vpl_execution",
        "vpl_evaluate.cases",
    ]


    keySourceFiles = None
    KEY_PROGRAM_NAME = "key_program"
    KEY_OUTFILE_NAME = "key_outfile"

    STUDENT_PROGRAM_NAME = "student_program"
    STUDENT_OUTFILE_NAME = "student_outfile"

    @classmethod
    def setUpClass(cls):
        abs_path_to_this_file = sys.modules[cls.__module__].__file__
        cls.THIS_DIR_NAME, cls.THIS_FILE_NAME = os.path.split(abs_path_to_this_file)

        if cls.keySourceFiles is None:
            warnings.warn("keySourceFiles unspecified! Assuming no key program. \nInitialize this class attribute to an empty list to silence this warning.")
            cls.keySourceFiles = []

        cls.compile_student_program()
        cls.compile_key_program()

        cls.subprocess_run_options = {
            "cwd"           : cls.THIS_DIR_NAME, # Needed for programs to write their output files to the right place.
            "env"           : os.environ.update({ "PATH" : os.environ["PATH"] + ":" + cls.THIS_DIR_NAME }),    # Needed to find the compiled files.
            "capture_output": True, 
            "text"          : True,
            "timeout"       : 10,
            "check"         : True, # Raise CalledProcessError on non-zero exit code.
        }
        cls.program_execution_env = cls.subprocess_run_options["env"]
        return super().setUpClass()


    @classmethod
    def compile_student_program(cls):
        student_source_files = [ 
            file for file in os.listdir(cls.THIS_DIR_NAME) 
            if file not in cls.keySourceFiles 
                    and file not in cls.VPL_SYSTEM_FILES
                    and file != cls.THIS_FILE_NAME
                    and not file.startswith("__")
        ]

        student_program = cls.detectLanguageAndMakeProgram(
            student_source_files, 
            cls.STUDENT_PROGRAM_NAME, 
            cls.STUDENT_OUTFILE_NAME
        )
        student_program.compile(cls.THIS_DIR_NAME)


    @classmethod
    def compile_key_program(cls):
        key_program = cls.detectLanguageAndMakeProgram(
            cls.keySourceFiles,
            cls.KEY_PROGRAM_NAME,
            cls.KEY_OUTFILE_NAME
        )
        if key_program is not None:
            key_program.compile(cls.THIS_DIR_NAME)

    
    @staticmethod
    def detectLanguageAndMakeProgram(file_list: list[str], executable_name: str, output_file_name: str) -> SupportedLanguageProgram:
        if file_list == []:
            return 

        current_program_lang = None
        current_program_class = None
        source_files = []
        for file in file_list:
            for supported_lang, lang_program_class in OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE.items():
                if current_program_lang is not None and current_program_lang != supported_lang:
                    break # We're already found our language, and this is not it.

                if current_program_lang is None and file.endswith(supported_lang.extension):
                    current_program_lang = supported_lang
                    current_program_class = lang_program_class
                    source_files.append(file)

                elif current_program_lang is not None and file.endswith(current_program_lang.extension):
                    source_files.append(file)

        # Call constructor for detected program class.
        return current_program_class(executable_name, source_files, output_file_name)
        

    @classmethod
    def tearDownClass(cls):
        '''
        Find all names of unittest.TestCase test_* methods, and write them to 
        a file in the same directory as the subclass of this.
        '''
        test_suite = unittest.defaultTestLoader.discover(cls.THIS_DIR_NAME)
        vpl_test_tuples = cls.makeVPLTestTuples(test_suite)
        findmodules.make_cases_file_from_list(
            cls.THIS_DIR_NAME,
            vpl_test_tuples,
            False
        )
        return super().tearDownClass()
    

    @classmethod
    def makeVPLTestTuples(cls, test_suite) -> list[tuple[str]]:
        '''
        Walks the TestSuite hierarchy looking for TestCase objects.
        When found, adds a tuple containing:
            tc.__module__
            tc.__class__.__name__
            tc._testMethodName
        to the list. Returns the list.
        '''
        vpl_test_tuples = []
        for test_item in test_suite._tests:
            if isinstance(test_item, unittest.TestSuite):
                vpl_test_tuples.extend(
                    cls.makeVPLTestTuples(test_item)
                )
            elif isinstance(test_item, unittest.TestCase):
                vpl_test_tuples.append(
                    (test_item.__module__, 
                     test_item.__class__.__name__, 
                     test_item._testMethodName)
                )
            else:
                raise TypeError(f"Bruh. I don't know what to do with a {test_item}")
            
        return vpl_test_tuples
    


        
    @classmethod
    def run_program_helper(cls, executable: str, cli_args: list[str], input_str: str):
        # subprocess_run_options = {
        #     "input"         : input_str,
        #     "cwd"           : cls.THIS_DIR_NAME, # Needed for programs to write their output files to the right place.
        #     "env"           : os.environ.update({ "PATH" : os.environ["PATH"] + ":" + cls.THIS_DIR_NAME }),    # Needed to find the compiled files.
        #     "capture_output": True, 
        #     "text"          : True,
        #     "timeout"       : 10,
        #     "check"         : True, # Raise CalledProcessError on non-zero exit code.
        # }
        # cls.program_execution_env = subprocess_run_options["env"]
        return subprocess.run([executable] + cli_args, input=input_str, **cls.subprocess_run_options)
    

    @classmethod
    def run_program(cls, cli_args: list[str], input_string: str):
        return cls.run_program_helper(cls.STUDENT_PROGRAM_NAME, cli_args, input_string)
    
    
    @classmethod
    def run_key_program(cls, cli_args: list[str], input_string: str):
        return cls.run_program_helper(cls.KEY_PROGRAM_NAME, cli_args, input_string)



# class VPLTestCase:
# class VPLCaseBlock:

#     CASE_TYPE_FOR_SEMANTIC = {
#         SemanticCaseType.FILE_CHECK             : (
#             VPLCaseType.RUN_FOR_FILE_GEN, 
#             VPLCaseType.FILE_COMPARISON,
#         ),
#         SemanticCaseType.OUTPUT_CHECK           : (
#             VPLCaseType.OUTPUT_COMPARISON,
#         ),
#         SemanticCaseType.FILE_AND_OUTPUT_CHECK  : (
#             VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP, 
#             VPLCaseType.FILE_COMPARISON,
#             )
#         }

#     CASE_NAME_COMMON_FORMAT = " with args {args_str}"
    
#     PROGRAM_ARGS_COMMON_FORMAT = " {args_str} "
    
#     # PYLINT_ARGS: List[str] = []
#     # PYLINT_ARGS = " ".join(PYLINT_ARGS)

#     VPL_CASE_TEMPLATES = {
#         VPLCaseType.OUTPUT_COMPARISON           :(
#               "Case = Output" + CASE_NAME_COMMON_FORMAT
#             + "\n    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT
#             + "\n    Output = \"{key_output}\""
#             + "\n    Grade reduction = 100%"
#             + "\n"
#         ),
#         VPLCaseType.RUN_FOR_FILE_GEN            :(
#               "Case = Run" + CASE_NAME_COMMON_FORMAT
#             + "\n    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT
#             + "\n    Grade reduction = 100%"
#             + "\n"
#         ),
#         VPLCaseType.RUN_FOR_FILE_GEN_OUTPUT_COMP:(
#               "Case = Check stdout, Generate file" + CASE_NAME_COMMON_FORMAT
#             + "\n    Program arguments =" + PROGRAM_ARGS_COMMON_FORMAT
#             + "\n    Output = \"{key_output}\""
#             + "\n    Grade reduction = 100%"
#             + "\n"
#         ),
#         VPLCaseType.FILE_COMPARISON             :(
#               "Case = Check output file" + CASE_NAME_COMMON_FORMAT
#             + "\n    Program to run = {file_comparison_program}"
#             + "\n    Program arguments = {key_output_file_name} {student_output_file_name}"
#             + "\n    Output = \"Empty diff. #noNewsIsGoodNews\""
#             + "\n    Grade reduction = 100%"
#             + "\n"
#         ),
#         VPLCaseType.PYTHON_UNITTEST             :(
#               "Case = {method_name}"
#             + "\n    Program to run = /usr/bin/python3"
#             + "\n    Program arguments = -m unittest{module_name}.{test_class}.{method_name}"
#             + "\n    Output = /.*OK/i"
#             + "\n"
#         ),
#         VPLCaseType.PYLINT_ANALYSIS             :(
#               "Case = PyLiny Style Check"
#             + "\n    Program to run = /usr/bin/python3"
#             + "\n    Program arguments = -m pylint {module_name}" # + " " + PYLINT_ARGS
#             + "\n    Output = /.*Your code has been rated at 10.00/10*/i"
#             + "\n    Grade reduction = 0%"
#             + "\n"
#         )
#     }
 
#     student_extension = "_student_results.txt"
#     key_file_extension = "_key_results.txt"


#     def __init__(self, 
#                  case_type: SemanticCaseType, 
#                  key_program: Callable,
#                  local_path_prefix: str,
#                  program_arguments: Tuple = (),
#                  outfile_index: int = None,
#                  key_outfile: str = "",
#                  program_uses_input: bool = True):

#         if program_uses_input and program_arguments == ():
#             raise ValueError("The program must have some arguments! Override with program_uses_input=False")

#         self.case_type = case_type
#         self.key_program = key_program
#         self.local_path_prefix = local_path_prefix
#         self.args = program_arguments
#         self.outfile_index = outfile_index
#         self.key_outfile = key_outfile
#         self.uses_input = program_uses_input

#         self.args_str = " ".join([str(arg) for arg in self.args])


#     def __repr__(self):
#         return f"VPLTestCase({self.case_type}, program_arguments={self.args}, outfile_index={self.outfile_index}, program_uses_input={self.uses_input}"
    

#     def get_output_file_basename(self):
#         return f"{self.args_str.replace(' ', '_')}"


#     def get_student_output_file_name(self):
#         if self.outfile_index is not None:
#             return os.path.basename(self.args[self.outfile_index])
#             # Do we need the basename() call?

#         return self.get_key_output_file_base_name() + self.student_extension
    

#     def get_key_output_file_name(self):
#             if self.key_outfile == "":
#                 return self.get_output_file_basename() + self.key_file_extension
        
#             return os.path.basename(self.key_outfile)
    
#     @staticmethod
#     def is_file_name(string):
#         if type(string) is not str:
#             return False
        
#         valid_file_endings = [
#             ".csv",
#             ".txt",
#         ]

#         return any(string.endswith(valid_ending) for valid_ending in valid_file_endings)
    

#     def add_local_path_prefix_to_file_names(self) -> Tuple:
#         modified_args = []
#         for arg in self.args:
#             if VPLTestCase.is_file_name(arg):
#                 modified_args.append(os.path.join(self.local_path_prefix, arg))
#             else:
#                 modified_args.append(arg)
        
#         return tuple(modified_args)
    

#     def get_key_output(self):
#         # Skip the expected output generation if it is not needed.
#         key_output = ""
        
#         if self.case_type in (SemanticCaseType.OUTPUT_CHECK,SemanticCaseType.FILE_AND_OUTPUT_CHECK):
#             with unittest.mock.patch("sys.stdout", new = StringIO()) as captured_output:
#                 args_with_abs_paths = self.add_local_path_prefix_to_file_names()
#                 self.key_program(*args_with_abs_paths)#,
#                             # os.path.join(self.local_path_prefix, self.infile))
#                 key_output = captured_output.getvalue()

#         return key_output
    

#     def get_case_file_args_string(self):
#         modified_args_list = []
#         for arg in self.args:
#             if type(arg) is str and self.is_file_name(arg):
#                 modified_args_list.append(
#                     os.path.basename(arg)
#                 )
#             else:
#                 modified_args_list.append(arg)

#         return " ".join([str(arg) for arg in modified_args_list])
    

#     def make_all_case_blocks(self):
#         all_case_blocks = ""
#         for case_type in self.CASE_TYPE_FOR_SEMANTIC[self.case_type]:

#             # Compile all the things that need to be substituted into the Case template.
#             template_placeholder_values = {
#                 "args_str"                  : self.get_case_file_args_string(),
#                 "student_output_file_name"  : self.get_student_output_file_name(),
#                 "key_output_file_name"      : self.get_key_output_file_name(),
#                 "key_output"                : self.get_key_output(),
#                 "file_comparison_program"   : "differ.sh",
#                 # vv Python-specific vv
#                 "method_name"               : "",
#                 "module_name"               : "",
#                 "test_class"                : "",
#             }

#             # Format the Case block and add it to the string 
#             case_block = self.VPL_CASE_TEMPLATES[case_type]
#             all_case_blocks += case_block.format(**template_placeholder_values) + "\n"

#         return all_case_blocks



if __name__ == "__main__":
    print("Are you lost? You look lost.")
