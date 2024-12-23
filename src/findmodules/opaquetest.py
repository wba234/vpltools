import os
import subprocess
import findmodules

__unittest = True

class OpaqueTest(findmodules.VPLTestCase):
    '''
    A class for testing programs as black boxes, with no visible internal structure.
    I.e., end-to-end testing. Provides automatic location of executable files.
    '''
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

    @classmethod
    def hasNonExecutableExtension(cls, file_name) -> bool:
        return any(file_name.endswith(extension) for extension in cls.NON_EXECUTABLE_EXTENSIONS)

    # Ignore these when searching for executable files.
    VPL_SYSTEM_FILES = [ 
        "vpl_test",
        ".vpl_tester",
        "vpl_execution",
    ]

    SUBPROCESS_RUN_OPTIONS = {
        "capture_output": True, 
        "text"          : True,
        "timeout"       : 10,
        "check"         : True, # Raise CalledProcessError on non-zero exit code.
    }

    MAIN_NAME = "main"
    SRC_EXTENSION = ".c"
    SRC_ERR = 42

    GCC_EXEC_NAME = "a.out"
    GCC_COMPILE = [ "gcc", "-lm", "-o", GCC_EXEC_NAME ]
    GCC_MAKE = [ "make" ]
    
    THIS_DIR_NAME: str = None


    @classmethod
    def findExecutables(cls) -> list[str]:
        '''
        Don't maintain a list of executables, or source files. 
        In theory, both of these could be generated automatically.
        '''
        possible_executables = []
        for file_name in os.listdir(cls.THIS_DIR_NAME):
            if not cls.hasNonExecutableExtension(file_name) and file_name not in cls.VPL_SYSTEM_FILES:
                possible_executables.append(file_name)

        return possible_executables


    @classmethod
    def findSourceFiles(cls) -> list[str]:
        '''
        Don't maintain a list of executables, or source files. 
        In theory, both of these could be generated automatically.
        '''
        return [ 
            file_name for file_name in os.listdir(cls.THIS_DIR_NAME) 
            if file_name.endswith(cls.SRC_EXTENSION) 
        ]


    @classmethod
    def compileOneFileOrMain(cls) -> int:
        '''
        Returns the return code from gcc, or cls.SOURCE_ERR, to indicate that source.
        Can only be called after setUpClass has initialized class attributes.
        '''
        source_files = cls.findSourceFiles()

        # Try to find main...
        try:
            main_index = source_files.index(cls.MAIN_NAME + cls.SRC_EXTENSION)
        except ValueError:
            # ...or the only one...
            if len(source_files) != 1:
                return cls.SRC_ERR
        
            main_index = 0
        
        # ...so it can be compiled.
        # gcc_command = cls.GCC_COMPILE + [os.path.join(cls.THIS_DIR_NAME, source_files[main_index])]
        gcc_command = cls.GCC_COMPILE + [source_files[main_index]]
        return subprocess.run(gcc_command, cwd=cls.THIS_DIR_NAME).returncode


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

        return subprocess.run(cls.GCC_COMPILE + source_files, cwd=cls.THIS_DIR_NAME).returncode


    @classmethod
    def compileWithMake(cls) -> int:
        '''
        Returns the return code from the command "make":
        0 : success
        2 : make encountered errors
        '''
        return subprocess.run(cls.GCC_MAKE, cwd=cls.THIS_DIR_NAME).returncode


    @classmethod
    def setUpClass(cls, attempt_compilation=True):
        '''
        Perform any needed setup before all classes.
        '''
        super().setUpClass() # Sets cls.THIS_DIR_NAME.

        executables = cls.findExecutables()
        if len(executables) != 1 and attempt_compilation:
            # Some things we can reasonably try to do to compile:
            # 0. Compile the only .c file found.
            # 1. Compile the main.c file, assume that it will #include the others.
            # 2. Compile all the .c files.
            # 3. Try to use the make utility.
            compilation_strategies = [ 
                cls.compileOneFileOrMain, 
                cls.compileAllSourceFiles, 
                cls.compileWithMake
            ]

            for compile in compilation_strategies:
                status = compile()
                if status == 0:
                    break
            
            executables = cls.findExecutables()


        if len(executables) != 1:
            raise RuntimeError(f"Couldn't automatically identify executable.\nCandidates: {executables}")
        
        cls.executable = os.path.join(cls.THIS_DIR_NAME, executables[0])
       

    @classmethod
    def getExecutable(cls):
        return cls.executable


    @classmethod
    def run_program(self, cli_args: list[str], input_string: str):
        return subprocess.run(
            [self.executable] + cli_args, 
            input=input_string, 
            cwd=os.path.dirname(self.THIS_DIR_NAME),
            **self.SUBPROCESS_RUN_OPTIONS
        )
    
    @classmethod
    def run_program_helper(self, executable: str, cli_args: list[str], input_str: str):
        return subprocess.run(
            [executable] + cli_args,
            input=input_str,
            cwd=os.path.dirname(self.THIS_DIR_NAME),
            **self.SUBPROCESS_RUN_OPTIONS
        )
    
    @classmethod
    def run_key_program(self, cli_args: list[str], input_string: str):
        return subprocess.run(
            [self.key_executable] + cli_args,

        )
