import os
import subprocess
from dataclasses import dataclass

import findmodules

__unittest = True


@dataclass
class SupportedLanguage:
    name: str
    extension: str


SUPPORTED_LANGUAGES = {
    "C"     : SupportedLanguage("C", ".c"),
    "CPP"   : SupportedLanguage("C++", ".cpp"),
    "JAVA"  : SupportedLanguage("Java", ".java"),
}


@dataclass
class SupportedLanguageProgram:
    language: SupportedLanguage
    compilation_commands: list[str]
    main_file_base_name: str
    executable_name: str
    source_files: list[str] = []
    output_file_name: str = None


class CProgram(SupportedLanguageProgram):
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["C"], "main", [ "gcc", "-lm", "-o"], executable_name, source_files, output_file_name)

    def compilationCommand(self):
        return self.compilation_commands + [self.executable_name] + self.source_files
    

class CPPProgram(SupportedLanguageProgram):
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["CPP"], "main", [ "g++", "-lm", "-o"], executable_name, source_files, output_file_name)

    def compilationCommand(self):
        return self.compilation_commands + [self.executable_name] + self.source_files
    

class JavaProgram(SupportedLanguageProgram):
    def __init__(self, executable_name, source_files, output_file_name):
        return super().__init__(SUPPORTED_LANGUAGES["JAVA"], "main", ["java"], executable_name, source_files, output_file_name)
    
    def compilationCommand(self):
        return self.compilation_commands + self.source_files
    

PROGRAM_FOR_LANGUAGE = {
    SUPPORTED_LANGUAGES["C"]    :   CProgram,
    SUPPORTED_LANGUAGES["CPP"]  :   CPPProgram,
    SUPPORTED_LANGUAGES["JAVA"] :   JavaProgram,
}


class OpaqueTest(findmodules.VPLTestCase):
    '''
    A class for testing programs as black boxes, with no visible internal structure.
    I.e., end-to-end testing. Provides automatic location of executable files.
    '''

    key_files = None

    @classmethod
    def setUpClass(cls):
        '''
        Attempt compilation of student submission, and key program, prior to running tests.
        '''
        super().setUpClass() # Sets cls.THIS_DIR_NAME.

        cls.compile_student_program()
        cls.compile_key_program()

        # # Student submission
        # executables = cls.findExecutables()
        # if len(executables) != 1 and attempt_compilation:
        #     # Some things we can reasonably try to do to compile:
        #     # 0. Compile the only .c file found.
        #     # 1. Compile the main.c file, assume that it will #include the others.
        #     # 2. Compile all the .c files.
        #     # 3. Try to use the make utility.
        #     compilation_strategies = [ 
        #         cls.compileOneFileOrMain, 
        #         cls.compileAllSourceFiles, 
        #         cls.compileWithMake
        #     ]

        #     for compile in compilation_strategies:
        #         status = compile()
        #         if status == 0:
        #             break
            
        #     executables = cls.findExecutables()


        # if len(executables) != 1:
        #     raise RuntimeError(f"Couldn't automatically identify executable.\nCandidates: {executables}")
        
        # cls.executable = os.path.join(cls.THIS_DIR_NAME, executables[0])
       

        # Key program.
        # for supported_language in cls.SUPPORTED_LANGUAGES:
        #     if 


    @classmethod
    def compile_student_program(cls):        
        # Some things we can reasonably try to do to compile:
        # 0. Compile the only .c file found.
        # 1. Compile the main.c file, assume that it will #include the others.
        # 2. Compile all the .c files.
        # 3. Try to use the make utility.
        source_files = cls.findSourceFiles()
        for key_source_file in source_files:
            source_files.remove(key_source_file)

        student_program_language = cls.detectLanguage(source_files)
        student_program = SUPPORTED_LANGUAGES[student_program_language](student_program_language, "student_program", source_files, "student_output")
        student_program.compile()
        # TODO: Move this vvv into this ^^^.
        compilation_strategies = [ 
            cls.compileOneFileOrMain, 
            cls.compileAllSourceFiles, 
            cls.compileWithMake
        ]

        for compile in compilation_strategies:
            status = compile()
            if status == 0:
                break
        
        executables = cls.findNonKeyExecutables()

        if len(executables) != 1:
            raise RuntimeError(f"Couldn't automatically identify executable.\nCandidates: {executables}")
        
        cls.executable = os.path.join(cls.THIS_DIR_NAME, executables[0])

    # @classmethod
    # def compile_key_program(cls):
    #     key_executables = os.listdir(cls.THIS_DIR_NAME)
    #     if cls.key_executable_name in key_executables:
    #         return
        
    #     compilation
            

    # A collection of common file extensions and items which should not be the executable.
    # This doesn't feel like a robust way to achieve this goal.
    NON_EXECUTABLE_EXTENSIONS = [
        ".c",
        ".h",
        ".cpp",
        ".hpp",
        ".sh",
        ".o",
        "makefile",
        ".html",
        ".cases",
        ".py",
        "__pycache__",
        ".old",
        ".txt",
        ".gif",
        ".DS_Store"
    ]


    # Ignore these when searching for executable files.
    VPL_SYSTEM_FILES = [ 
        "vpl_test",
        ".vpl_tester",
        "vpl_execution",
    ]

    # detected_language = None

    # key_program_files = None
    # key_executable_name = "key_program"

    THIS_DIR_NAME: str = None

    # MAIN_NAME = "main"
    # SRC_EXTENSION = ".c"
    SRC_ERR = 42
    # GCC_EXEC_NAME = "a.out"
    # GCC_MAKE = [ "make" ]

    @classmethod
    def detectLanguage(cls, file_list=[]) -> SupportedLanguage:
        '''
        Compare each element in file_list (or the directory of the child test class)
        to determine if if corresponds to one of the languages supported by OpaqueTest.
        Uses the first matching extension found.
        '''
        if not file_list:
            file_list = os.listdir(cls.THIS_DIR_NAME)

        for file_name in file_list:
            for supported_language in cls.SUPPORTED_LANGUAGES:
                if file_name.endswith(supported_language.extension):
                    return supported_language
        
        raise RuntimeError("Unsupported language!")


    @classmethod
    def hasNonExecutableExtension(cls, file_name) -> bool:
        return any(file_name.endswith(extension) for extension in cls.NON_EXECUTABLE_EXTENSIONS)
       

    @classmethod
    def findNonKeyExecutables(cls) -> list[str]:
        '''
        Don't maintain a list of executables, or source files. 
        In theory, both of these could be generated automatically.
        '''
        # assert cls.key_program is not None, "You must supply a key program name!"
        possible_executables = []
        for file_name in os.listdir(cls.THIS_DIR_NAME):
            if (not cls.hasNonExecutableExtension(file_name) 
                    and file_name not in cls.VPL_SYSTEM_FILES
                    and file_name != cls.key_executable_name):
                possible_executables.append(file_name)

        return possible_executables


    @classmethod
    def findSourceFiles(cls) -> list[str]:
        '''
        Don't maintain a list of executables, or source files. 
        In theory, both of these could be generated automatically.
        '''
        source_files = []
        this_dir_files = os.listdir(cls.THIS_DIR_NAME)
        cls.detected_language = cls.detectLanguage(this_dir_files)

        for file_name in this_dir_files:
            if cls.detected_language is not None and file_name.endswith(cls.detected_language.extension):
                source_files.append(file_name)

        return source_files


    @classmethod
    def compileOneFileOrMain(cls) -> int:
        '''
        Returns the return code from gcc, or cls.SOURCE_ERR, to indicate that source.
        Can only be called after setUpClass has initialized class attributes.
        '''
        source_files = cls.findSourceFiles()
        
        # Try to find main...
        try:
            # main_index = source_files.index(cls.MAIN_NAME + cls.SRC_EXTENSION)
            main_index = source_files.index(cls.detected_language.main_file_base_name + cls.detected_language.extension)
        except ValueError:
            # ...or the only one...
            if len(source_files) != 1:
                return cls.SRC_ERR
        
            main_index = 0
        
        # ...so it can be compiled.
        # gcc_command = cls.GCC_COMPILE + [os.path.join(cls.THIS_DIR_NAME, source_files[main_index])]
        # gcc_command = cls.GCC_COMPILE + [source_files[main_index]]
        compile_command = cls.detected_language.compilation_commands + [source_files[main_index]]
        return subprocess.run(compile_command, cwd=cls.THIS_DIR_NAME).returncode


    @classmethod
    def compileAllSourceFiles(cls) -> int:
        '''
        Returns the return code from gcc, or raises ValueError.
        Can only be called after setUpClass has initialized class attributes.
        '''
        source_files = cls.findSourceFiles()
        if not source_files:
            return cls.SRC_ERR
        
        for i in range(len(source_files)):
            source_files[i] = os.path.join(cls.THIS_DIR_NAME, source_files[i])
        # return subprocess.run(cls.GCC_COMPILE + source_files, cwd=cls.THIS_DIR_NAME).returncode
        return subprocess.run(cls.detected_language.compilation_commands + source_files, cwd=cls.THIS_DIR_NAME)


    @classmethod
    def compileWithMake(cls) -> int:
        '''
        Returns the return code from the command "make":
        0 : success
        2 : make encountered errors
        '''
        # return subprocess.run(cls.GCC_MAKE, cwd=cls.THIS_DIR_NAME).returncode
        return subprocess.run(cls.detected_language.make, cwd=cls.THIS_DIR_NAME).returncode






    @classmethod
    def getExecutable(cls):
        return cls.executable


    SUBPROCESS_RUN_OPTIONS = {
        "capture_output": True, 
        "text"          : True,
        "timeout"       : 10,
        "check"         : True, # Raise CalledProcessError on non-zero exit code.
    }
        
    @classmethod
    def run_program_helper(cls, executable: str, cli_args: list[str], input_str: str):
        return subprocess.run(
            [executable] + cli_args,
            input=input_str,
            cwd=os.path.dirname(cls.THIS_DIR_NAME),
            **cls.SUBPROCESS_RUN_OPTIONS
        )
    

    @classmethod
    def run_program(cls, cli_args: list[str], input_string: str):
        return cls.run_program_helper(cls.executable, cli_args, input_string)
    
    
    @classmethod
    def run_key_program(cls, cli_args: list[str], input_string: str):
        return cls.run_program_helper(cls.key_executable, cli_args, input_string)
