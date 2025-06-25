import abc
import sys
import unittest
import subprocess
import os.path
import warnings
import importlib
import re
import enum
from typing import Type
from types import FunctionType
from copy import copy
from dataclasses import dataclass
import contextlib

import vpltools

__unittest = True

class NoProgramError(RuntimeError):
    pass

class UnsupportedFeatureError(RuntimeError):
    pass

@dataclass
class SupportedLanguage(abc.ABC):
    name: str
    extension: str

    def __hash__(self):
        '''
        Provided to that this can be used as the key in a dictionary.
        '''
        return hash(self.name)


# @dataclass
class SupportedLanguageProgram(abc.ABC):
    '''
    Represents a program written in one of the languages supported by this package.
    This is an abstract base class, which is not instantiated directly. It is intended
    to be extended into another class for each supported language.
    '''
    def __init__(self, 
                 language: SupportedLanguage, 
                 compilation_commands: list[str], 
                 main_file_base_name: str, 
                 executable_dir: str,
                 executable_name: str,
                 source_files: list[str],
                 output_file_name: str) -> None:
        self.language = language
        self.compilation_commands = compilation_commands
        self.main_file_base_name = main_file_base_name
        self.executable_dir = executable_dir
        self.executable_name = executable_name
        self.source_files = source_files
        self.output_file_name = output_file_name


    @abc.abstractmethod
    def compilationCommand(self):
        '''
        Abstract method to ensure individual languages implement their respective 
        compilation commands. These should raise RunTimeError if compilation fails.
        '''
        raise NotImplementedError


    def compile(self, use_dir, recompile=False):
        '''
        Compile the program represented by the calling object. If the target program
        already exists, compilation is skipped, unless the recompile flag is set.
        '''
        if os.path.exists(os.path.join(self.executable_dir, self.executable_name)) and not recompile:
            return
        
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
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        return super().__init__(
            SupportedLanguages.C, # type: ignore
            [ "gcc", "-o", executable_name ] + source_files + ["-lm"], 
            "main", 
            executable_dir,
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
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        return super().__init__(
            SupportedLanguages.CPP, # type: ignore
            [ "g++", "-o", executable_name] + source_files + ["-lm"], 
            "main", 
            executable_dir,
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
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        '''
        Note that executable_name
        '''
        super().__init__(SupportedLanguages.Java, ["javac"], "main", executable_dir, executable_name, source_files, output_file_name) # type: ignore
        self.find_main_and_set_exec_name()
    

    def compilationCommand(self):
        for source_file in self.source_files:
            with open(os.path.join(self.executable_dir, source_file), "r") as fp:
                file_contents = fp.read()
                if re.search("^\\s*package\\s*.*;", file_contents, flags=re.MULTILINE) is not None:
                    raise UnsupportedFeatureError("Running Java packages is not supported by vpltools. Please remove the package statements.")

        return self.compilation_commands + self.source_files


    def run(self, cli_args, input="", **kwargs):
        return subprocess.run(["java", self.executable_name, *cli_args], input=input, **kwargs)
    

    def find_main_and_set_exec_name(self) -> str:
        for file in self.source_files:
            with open(os.path.join(self.executable_dir, file), "r") as fo:
                main_matches = re.findall(r"public\s+static\s+void\s+main", fo.read())
                if main_matches:
                    self.executable_name = file.split(".")[0]
                    return self.executable_name
        raise NoProgramError("Java program has no (public static void) main function!")



class PythonProgram(SupportedLanguageProgram):
    '''
    Represents a program written in Python,
    e.g., a student's submission, or an instructor's key program.
    '''
    PYTHON_COMMAND = "python3"
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        exec_name = ""
        if len(source_files) == 0:
            raise ValueError("No input files found!")
        elif len(source_files) == 1:
            exec_name = source_files[0]
        elif len(source_files) > 1:
            if "main" in source_files:
                exec_name = source_files[source_files.index("main")]
            else:
                raise ValueError(f"If you have more than 1 file, you must name one of them main.py! Found {source_files}")

        return super().__init__(
            SupportedLanguages.Python, # type: ignore
            [],
            executable_dir,
            exec_name,
            source_files[0], 
            source_files, 
            output_file_name=None) # type: ignore


    def compilationCommand(self):
        return None
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.PYTHON_COMMAND, self.executable_name, *cli_args], input=input, **kwargs)



class SQLQuery(SupportedLanguageProgram):
    '''
    Represents a SELECT query, written in SQL. Could be some other
    statement which produces a result set.
    '''
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
            if len(source_files) != 1:
                raise ValueError("Too many SQL files! Only one SQL file is supported. Found:\n {source_files}")
            super().__init__(
                SupportedLanguages.SQL, # type: ignore
                [],
                "",
                executable_dir,
                executable_name,
                source_files,
                output_file_name
            )


    def compilationCommand(self):
        return None
    
    
    def run(self, cli_args, input="", **kwargs): # type: ignore
        return None
    
    

class SupportedLanguages(enum.Enum):
    C = SupportedLanguage("C", ".c")
    CPP = SupportedLanguage("C++", ".cpp")
    Java = SupportedLanguage("Java", ".java")
    Python = SupportedLanguage("Python", ".py")
    SQL = SupportedLanguage("SQL", ".sql")

# SUPPORTED_LANGUAGES = {
#     "C"     : SupportedLanguages.C,
#     "CPP"   : SupportedLanguages.CPP,
#     "JAVA"  : SupportedLanguages.Java,
#     "PYTHON": SupportedLanguages.Python
# }


OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE: dict[SupportedLanguages, Type[SupportedLanguageProgram]] = {
    SupportedLanguages.C        :   CProgram,
    SupportedLanguages.CPP      :   CPPProgram,
    SupportedLanguages.Java     :   JavaProgram,
    SupportedLanguages.Python   :   PythonProgram,
    SupportedLanguages.SQL      :   SQLQuery
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
        ".vpl_launcher.sh",
        "vpl_execution",
        "vpl_evaluate.cases",
        "common_script.sh",
        "vpl_environment.sh",
        "vpl_compilation_error.txt",
    ]

    NON_EXECUTABLE_EXTENSIONS = [
        ".pdf",
        ".jpeg",
        ".jpg",
        ".svg",
    ]

    key_source_files: list[str] | None = None   # type: ignore
    ignore_files: list[str] = []
    ignore_extensions = []
    
    permitted_student_languages = list(SupportedLanguages)

    run_basic_tests = []
    # skip_basic_tests = vpltools.BASIC_TESTS
    include_pylint = False

    make_vpl_evaluate_cases_file = True

    mask_extension = ".save"
    files_renamed: list[tuple[str, str]] = [] # old name, new_name

    key_program_name = "key_program"
    key_outfile_name = "key_outfile"

    student_program_name = "student_program"
    student_outfile_name = "student_outfile"

    student_program: SupportedLanguageProgram
    key_program: SupportedLanguageProgram | None = None

    @classmethod
    def set_this_dir_name(cls):
        abs_path_to_this_file = sys.modules[cls.__module__].__file__
        cls.THIS_DIR_NAME, cls.THIS_FILE_NAME = os.path.split(abs_path_to_this_file) # type: ignore
    

    @classmethod
    def setUpClass(cls):
        '''
        Locates student and key modules, compiling if necessary.
        Imports python modules, and runs basic tests on student modules.
        '''
        cls.set_this_dir_name()

        if cls.key_source_files is None:
            warnings.warn("key_source_files unspecified! Assuming no key program. \nInitialize this class attribute to an empty list to silence this warning.")
            cls.key_source_files: list[str] = []

        cls.student_program = cls.compile_student_program()
        cls.key_program = cls.compile_key_program()

        cls.subprocess_run_options = {
            "cwd"           : cls.THIS_DIR_NAME, # Needed for programs to write their output files to the right place.
            "env"           : copy(os.environ),
            "capture_output": True, 
            "text"          : True,
            # "timeout"       : 15,
            # "check"         : True, # Raise CalledProcessError on non-zero exit code. 
            # ^^ Removed, so that subclasses have error handling, reporting responsibility.
            #    This package should not be noticed. As the penguins say; "You didn't see anything..."
        }
        # Add current directory to PATH, so we can find our compiled binaries.
        cls.subprocess_run_options["env"].update({ "PATH" : os.environ["PATH"] + ":" + cls.THIS_DIR_NAME })

        # Add this as a class attribute, so others can find it; e.g. to use pexpect.spawn.
        cls.program_execution_env = cls.subprocess_run_options["env"]

        # If the student program is a Python program, import it as a module.
        cls.student_py_module = cls.import_as_py_module(cls.student_program, cls.run_basic_tests)
        cls.key_py_module = cls.import_as_py_module(cls.key_program)

        return super().setUpClass()


    @classmethod
    def import_as_py_module(cls, program: SupportedLanguageProgram | None, run_basic_tests: list[FunctionType] = []):
        '''
        Returns a module object if program is a Python program, None otherwise. 
        None will also be returned if the import fails for any reason. This can happen 
        if a Python script which expects arguments (which will not be supplied during import).
        Runs each of the basic tests supplied.
        '''
        if not isinstance(program, PythonProgram):
            return None
        
        null_dev = open(os.devnull, "w")
        try:
            with contextlib.redirect_stdout(null_dev):
                module = importlib.import_module(os.path.splitext(program.executable_name)[0])
                # I don't want any output from student modules when importing.
        except: # In ANY part of the import fails, then return None.
            null_dev.close()
            return None
        
        null_dev.close()

        vpltools.run_basic_tests(module, run_basic_tests)
        return module

    

    @classmethod
    def find_student_files(cls) -> list[str]:
        # if override_THIS_DIR_NAME is not None:
            # cls.THIS_DIR_NAME = override_THIS_DIR_NAME
        return [ file for file in os.listdir(cls.THIS_DIR_NAME) 
                if file not in cls.key_source_files 
                    and file not in cls.ignore_files
                    and file not in cls.VPL_SYSTEM_FILES
                    and file != cls.THIS_FILE_NAME
                    and not file.startswith("__")
                    and not any(file.endswith(nee) for nee in cls.NON_EXECUTABLE_EXTENSIONS)
                    and not any(file.endswith(ife) for ife in cls.ignore_extensions)]


    @classmethod
    def compile_student_program(cls, recompile=False) -> SupportedLanguageProgram:
        '''
        Language-agnostic logic for finding an compiling student programs. 
        Returns a SupportedLanguageProgram object which can be used to 
        invoke the program.
        '''
        student_source_files = cls.find_student_files()
        student_program = cls.detectLanguageAndMakeProgram(
            student_source_files, 
            cls.student_program_name, 
            cls.student_program_name,
            unmask_hidden_files=False
        )
        student_program.compile(cls.THIS_DIR_NAME, recompile=recompile)

        if student_program.language not in cls.permitted_student_languages:
            raise NoProgramError(f"{student_program.language.name} is not permitted for this assignment. Options are: {", ".join(pl.name for pl in cls.permitted_student_languages)}")
        
        print("Stu program:", *student_program.source_files)
        return student_program


    @classmethod
    def compile_key_program(cls, recompile=False) -> SupportedLanguageProgram | None:
        '''
        Language-agnostic logic for finding an compiling key programs. 
        Returns a SupportedLanguageProgram object which can be used to 
        invoke the program.
        '''
        key_program = cls.detectLanguageAndMakeProgram(
            cls.key_source_files,
            cls.key_program_name,
            cls.key_outfile_name,
            unmask_hidden_files=True
        )
        if key_program is not None:
            key_program.compile(cls.THIS_DIR_NAME, recompile=recompile)
            print("Key program:", *key_program.source_files)
            return key_program


    @classmethod
    def unmask_hidden_files(cls, file_list: list[str]) -> None:
        '''
        To avoid encountering problems with VPL's standard compilation
        behavior, we can't have multiple files with valid extensions 
        containing main functions. Key files will be manually renamed
        (when provided) with a second extension to mask the desired one.
        This function removes all masking extensions, in place.
        '''
        for i in range(len(file_list)):
            if file_list[i].endswith(cls.mask_extension):
                new_name = file_list[i][:-len(cls.mask_extension)]
                os.rename(
                    os.path.join(cls.THIS_DIR_NAME, file_list[i]),
                    os.path.join(cls.THIS_DIR_NAME, new_name))
                cls.files_renamed.append((file_list[i] , new_name))
                file_list[i] = new_name


    @classmethod
    def detectLanguageAndMakeProgram(cls, file_list: list[str], executable_name: str, output_file_name: str, unmask_hidden_files: bool=False) -> SupportedLanguageProgram:
        '''
        Searches file_list for items which have the extension of a supported programming language, 
        using the first match found. Returns an object of the appropriate 
        SupportedLanguageProgram subclass.
        '''
        if file_list == []:
            raise NoProgramError("Program not found!")

        current_program_lang: SupportedLanguages = None         # type: ignore
        current_program_class: SupportedLanguageProgram = None  # type: ignore
        source_files = []
        
        if unmask_hidden_files:
            cls.unmask_hidden_files(file_list)

        for file in file_list:
            for supported_lang, lang_program_class in OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE.items():
                if current_program_lang is not None and current_program_lang != supported_lang:
                    continue # We're already found our language, and this is not it.

                if current_program_lang is None and file.endswith(supported_lang.value.extension):
                    current_program_lang = supported_lang
                    current_program_class = lang_program_class
                    source_files.append(file)

                elif current_program_lang is not None and file.endswith(current_program_lang.value.extension):
                    source_files.append(file)

        # Call constructor for detected program class.
        if current_program_class is None:
            raise FileNotFoundError(f"No submission found, or couldn't infer programming language! Found files: {file_list}")
        
        executable_name += "_" + os.path.splitext(source_files[0])[0]
        return current_program_class(cls.THIS_DIR_NAME, executable_name, source_files, output_file_name) # type: ignore


    @classmethod
    def remask_hidden_files(cls):
        for old_name, new_name in cls.files_renamed:
            os.rename(
                os.path.join(cls.THIS_DIR_NAME, new_name),
                os.path.join(cls.THIS_DIR_NAME, old_name)
            )


    @classmethod
    def tearDownClass(cls):
        '''
        Find all names of unittest.TestCase test_* methods, and write them to 
        a file in the same directory as the subclass of this.
        '''
        if cls.make_vpl_evaluate_cases_file: 
            test_suite = unittest.defaultTestLoader.discover(cls.THIS_DIR_NAME)
            vpl_test_tuples = cls.makeVPLTestTuples(test_suite)
            vpltools.make_cases_file_from_list(
                cls.THIS_DIR_NAME,
                vpl_test_tuples,
                cls.include_pylint if isinstance(cls.student_program, PythonProgram) else False
            )

        cls.remask_hidden_files()
        return super().tearDownClass()
    

    @classmethod
    def makeVPLTestTuples(cls, test_suite: unittest.TestSuite) -> list[tuple[str, str, str]]:
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
    

    def run_student_program(self, cli_args: list[str], input_string: str, **more_subprocess_run_kwargs):
        '''
        Execute the student's program in a subprocess, providing the given arguments, and 
        input string. Uses the environment of the calling VPLTestCase subclass.
        '''
        if self.student_program is None:
            raise NoProgramError("Student program not found!")

        # A few things could go wrong here. You could be testing on multiple machines, and 
        # and your Git repo contains an old executable which is not compatible with the 
        # current machine. This raises OSError, so recompile and try again.
        # Another potential problem is that the program runs, but experiences some kind of 
        # runtime error. This is not raised as an exception (see the subprocess_run_options)
        # but it does mean that we should fail the current test, and log the error to stdout.
        try:
            student_process = self.student_program.run(cli_args, input=input_string, **self.subprocess_run_options, **more_subprocess_run_kwargs)
        except OSError: # Existing executable, wrong architecture?
            self.student_program.compile(self.THIS_DIR_NAME, recompile=True)
            student_process = self.student_program.run(cli_args, input=input_string, **self.subprocess_run_options, **more_subprocess_run_kwargs)
        
        if student_process.returncode != 0:
            self.fail(msg=(f"\n\nYOUR PROGRAM CRASHED WITH THE COMMAND:\n"
                + f"> {' '.join(student_process.args)}\n\n"
                + "Verify that the command above works offline.\n\n"
                + f"ERROR MESSAGE FROM YOUR PROGRAM:\n"
                + "> " + student_process.stderr.replace("\n", "\n> ")))

        return student_process
    

    def run_key_program(self, cli_args: list[str], input_string: str, **more_subprocess_run_kwargs):
        '''
        Execute the key program in a subprocess, providing the given arguments, and 
        input string. Uses the environment of the calling VPLTestCase subclass.
        '''
        if self.key_program is None:
            raise NoProgramError("Key program not found!")

        # A few things could go wrong here. See run_student_program for details.
        try:
            key_process = self.key_program.run(cli_args, input=input_string, **self.subprocess_run_options, **more_subprocess_run_kwargs)
        except OSError: # Existing executable, wrong architecture?
            self.key_program.compile(self.THIS_DIR_NAME, recompile=True)
            key_process = self.key_program.run(cli_args, input=input_string, **self.subprocess_run_options, **more_subprocess_run_kwargs)

        if key_process.returncode != 0:
            self.fail(msg=(f"!!! THE KEY PROGRAM CRASHED WITH THE COMMAND:\n"
                + f"> {key_process.args}\n"
                + "!!! Send this error message in an email to your instructor.\n"
                + "!!! You may be eligible to collect a bug bounty.\n\n"
                + "ERROR MESSAGE FROM KEY PROGRAM:\n"
                + "> " + key_process.stderr.replace("\n", "\n> ")))

        return key_process

if __name__ == "__main__":
    print("Are you lost? You look lost.")
