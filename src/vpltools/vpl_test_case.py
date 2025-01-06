import abc
import sys
import unittest
import subprocess
import os.path
import warnings
import importlib
from types import FunctionType
from copy import copy
from dataclasses import dataclass

import vpltools

__unittest = True


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
        '''
        Compile the program represented by the calling object.
        '''
        command = self.compilationCommand()

        # Interpreted languages don't need compilation
        if command is None:
            return
        
        # Try the supplied compilation command
        compilation_process = subprocess.run(
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


    @abc.abstractmethod
    def run(self, cli_args: list[str], input="", **kwargs) -> subprocess.CompletedProcess:
        '''
        Executes the program represented by the calling object in a subprocess.
        '''
        raise NotImplementedError
        


class CProgram(SupportedLanguageProgram):
    '''
    Represents a program written in C, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_name: str, source_files: list[str], output_file_name: str):
        return super().__init__(
            SUPPORTED_LANGUAGES["C"], 
            [ "gcc", "-o", executable_name ] + source_files + ["-lm"], 
            "main", 
            executable_name, 
            source_files, 
            output_file_name)


    def compilationCommand(self):
        return self.compilation_commands
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.executable_name, *cli_args], input=input, **kwargs)

    

class CPPProgram(SupportedLanguageProgram):
    '''
    Represents a program written in C++, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_name: str, source_files: list[str], output_file_name: str):
        return super().__init__(
            SUPPORTED_LANGUAGES["CPP"], 
            [ "g++", "-o", executable_name] + source_files + ["-lm"], 
            "main", 
            executable_name, 
            source_files, 
            output_file_name)


    def compilationCommand(self):
        return self.compilation_commands
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.executable_name, *cli_args], input=input, **kwargs)
    


class JavaProgram(SupportedLanguageProgram):
    '''
    Represents a program written in Java, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["JAVA"], ["java"], "main", executable_name, source_files, output_file_name)
    

    def compilationCommand(self):
        return self.compilation_commands + self.source_files


    def run(self, cli_args, input="", **kwargs):
        return subprocess.run(["java", self.executable_name, *cli_args], input=input, **kwargs)
    


class PythonProgram(SupportedLanguageProgram):
    '''
    Represents a program written in Python,
    e.g., a student's submission, or an instructor's key program.
    '''
    PYTHON_COMMAND = "python3"
    def __init__(self, executable_name: str, source_files: list[str], output_file_name: str):
        if len(source_files) == 0:
            raise ValueError("No input files found!")
        elif len(source_files) == 1:
            exec_name = source_files[0]
        elif len(source_files) > 1:
            if "main" in source_files:
                exec_name = source_files.index("main")
            else:
                raise ValueError("If you have more than 1 file, you must name one of them main.py!")

        return super().__init__(
            SUPPORTED_LANGUAGES["PYTHON"], 
            [], 
            exec_name,
            source_files[0], 
            source_files, 
            output_file_name=None)


    def compilationCommand(self):
        return None
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.PYTHON_COMMAND, self.executable_name, *cli_args], input=input, **kwargs)
    

SUPPORTED_LANGUAGES = {
    "C"     : SupportedLanguage("C", ".c"),
    "CPP"   : SupportedLanguage("C++", ".cpp"),
    "JAVA"  : SupportedLanguage("Java", ".java"),
    "PYTHON": SupportedLanguage("Python", ".py")
}


OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE = {
    SUPPORTED_LANGUAGES["C"]    :   CProgram,
    SUPPORTED_LANGUAGES["CPP"]  :   CPPProgram,
    SUPPORTED_LANGUAGES["JAVA"] :   JavaProgram,
    SUPPORTED_LANGUAGES["PYTHON"]:  PythonProgram,
}


class VPLTestCase(unittest.TestCase):
    '''
    VPLTestCase provides most of the key functionality of vpltools.
    - locates student submissions in the directory containing it's subclasses,
    - automatically imports Python program as modules,
    - compiles files automatically, and 
    - provides the ability to run key and student programs in subprocesses.

    BEST PRACTICES WHEN SUBCLASSING:
    - explicitly set these class attributes:
        - key_source_files  : list of files which constitute the instructor solution
        - ignore_files      : list of files which should be ignored by vpltools 
                              (e.g., starter code, alternative solutions)
        - skip_basic_tests  : (Python submissions only) list of tests which should be 
                              skipped when importing student solutions. Basic tests are 
                              not run on Instructor solutions.
        - include_pylint    : (Python submissions only) boolean flag indicating if a
                              Pylint case should be added to vpl_evaluate.cases.
    '''
    VPL_SYSTEM_FILES = [ 
        "vpl_test",
        ".vpl_tester",
        "vpl_execution",
        "vpl_evaluate.cases",
    ]

    key_source_files = None
    ignore_files = []
    skip_basic_tests = []
    include_pylint = False


    KEY_PROGRAM_NAME = "key_program"
    KEY_OUTFILE_NAME = "key_outfile"

    STUDENT_PROGRAM_NAME = "student_program"
    STUDENT_OUTFILE_NAME = "student_outfile"

    @classmethod
    def setUpClass(cls):
        '''
        Locates student and key modules, compiling if necessary.
        Imports python modules, and runs basic tests on student modules.
        '''
        abs_path_to_this_file = sys.modules[cls.__module__].__file__
        cls.THIS_DIR_NAME, cls.THIS_FILE_NAME = os.path.split(abs_path_to_this_file)

        if cls.key_source_files is None:
            warnings.warn("key_source_files unspecified! Assuming no key program. \nInitialize this class attribute to an empty list to silence this warning.")
            cls.key_source_files = []

        cls.student_program = cls.compile_student_program()
        cls.key_program = cls.compile_key_program()

        cls.subprocess_run_options = {
            "cwd"           : cls.THIS_DIR_NAME, # Needed for programs to write their output files to the right place.
            "env"           : copy(os.environ),
            "capture_output": True, 
            "text"          : True,
            # "timeout"       : 15,
            "check"         : True, # Raise CalledProcessError on non-zero exit code.
        }
        # Add current directory to PATH, so we can find our compiled binaries.
        cls.subprocess_run_options["env"].update({ "PATH" : os.environ["PATH"] + ":" + cls.THIS_DIR_NAME }),

        # Add this as a class attribute, so others can find it; e.g. to use pexpect.spawn.
        cls.program_execution_env = cls.subprocess_run_options["env"]

        # If the student program is a Python program, import it as a module.
        cls.student_py_module = cls.import_as_py_module(cls.student_program, cls.skip_basic_tests)
        cls.key_py_module = cls.import_as_py_module(cls.key_program)

        return super().setUpClass()


    @classmethod
    def import_as_py_module(cls, program: SupportedLanguageProgram, skip_basic_tests: list[FunctionType] = []):
        '''
        Returns a module object if program is a Python program, None otherwise. 
        Runs basic tests if flag is set.
        '''
        if isinstance(program, PythonProgram):
            module = importlib.import_module(os.path.splitext(program.executable_name)[0])
            vpltools.run_basic_tests(module, skip_basic_tests)
            return module
        
        return None
    

    @classmethod
    def compile_student_program(cls):
        '''
        Language-agnostic logic for finding an compiling student programs. 
        Returns a SupportedLanguageProgram object which can be used to 
        invoke the program.
        '''
        student_source_files = [ 
            file for file in os.listdir(cls.THIS_DIR_NAME) 
            if file not in cls.key_source_files 
                    and file not in cls.ignore_files
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
        return student_program


    @classmethod
    def compile_key_program(cls):
        '''
        Language-agnostic logic for finding an compiling key programs. 
        Returns a SupportedLanguageProgram object which can be used to 
        invoke the program.
        '''
        key_program = cls.detectLanguageAndMakeProgram(
            cls.key_source_files,
            cls.KEY_PROGRAM_NAME,
            cls.KEY_OUTFILE_NAME
        )
        if key_program is not None:
            key_program.compile(cls.THIS_DIR_NAME)
            return key_program
    

    @staticmethod
    def detectLanguageAndMakeProgram(file_list: list[str], executable_name: str, output_file_name: str) -> SupportedLanguageProgram:
        '''
        Searches file_list for items which have the extension of a supported programming language, 
        using the first match found. Returns an object of the appropriate 
        SupportedLanguageProgram subclass.
        '''
        if file_list == []:
            return 

        current_program_lang = None
        current_program_class = None
        source_files = []
        for file in file_list:
            for supported_lang, lang_program_class in OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE.items():
                if current_program_lang is not None and current_program_lang != supported_lang:
                    continue # We're already found our language, and this is not it.

                if current_program_lang is None and file.endswith(supported_lang.extension):
                    current_program_lang = supported_lang
                    current_program_class = lang_program_class
                    source_files.append(file)

                elif current_program_lang is not None and file.endswith(current_program_lang.extension):
                    source_files.append(file)

        # Call constructor for detected program class.
        if current_program_class is None:
            raise FileNotFoundError(f"No submission found, or couldn't infer programming language! Found files: {file_list}")
        return current_program_class(executable_name, source_files, output_file_name)


    @classmethod
    def tearDownClass(cls):
        '''
        Find all names of unittest.TestCase test_* methods, and write them to 
        a file in the same directory as the subclass of this.
        '''
        test_suite = unittest.defaultTestLoader.discover(cls.THIS_DIR_NAME)
        vpl_test_tuples = cls.makeVPLTestTuples(test_suite)
        vpltools.make_cases_file_from_list(
            cls.THIS_DIR_NAME,
            vpl_test_tuples,
            cls.include_pylint if isinstance(cls.student_program, PythonProgram) else False
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
                warnings.warn(f"Ignoring non-test object {test_item}, of type {type(test_item)}.")
            
        return vpl_test_tuples
    

    @classmethod
    def run_student_program(cls, cli_args: list[str], input_string: str, **more_subprocess_run_kwargs):
        '''
        Execute the student's program in a subprocess, providing the given arguments, and 
        input string. Uses the environment of the calling VPLTestCase subclass.
        '''
        return cls.student_program.run(cli_args, input=input_string, **cls.subprocess_run_options, **more_subprocess_run_kwargs)
    
    
    @classmethod
    def run_key_program(cls, cli_args: list[str], input_string: str, **more_subprocess_run_kwargs):
        '''
        Execute the key program in a subprocess, providing the given arguments, and 
        input string. Uses the environment of the calling VPLTestCase subclass.
        '''
        return cls.key_program.run(cli_args, input=input_string, **cls.subprocess_run_options, **more_subprocess_run_kwargs)


if __name__ == "__main__":
    print("Are you lost? You look lost.")
