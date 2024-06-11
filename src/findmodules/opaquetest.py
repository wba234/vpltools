import unittest
import os
import subprocess
import findmodules

class OpaqueTest(unittest.TestCase):
    '''
    A class for testing programs as black boxes, with no visible internal structure.
    Provides automatic location of executable binary files.
    '''
    # A collection of common file extensions and items which should not be the executable.
    # This is not a robuse way to achieve this goal.
    NON_EXECUTABLE_EXTENTIONS = [
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
    ]

    SUBPROCESS_RUN_OPTIONS = {
        "capture_output": True, 
        "text"          : True,
        "timeout"       : 10,
        "check"         : True, # Raise CalledProcessError on non-zero exit code.
    }
    
    SUBCLASS_FILE = None


    @classmethod
    def setUpClass(cls):
        '''
        Perform any needed setup before all classes.
        '''
        this_dir_name = os.path.dirname(os.path.abspath(cls.SUBCLASS_FILE))
        executables = [ 
            file_name for file_name in os.listdir(this_dir_name) 
            if not any(file_name.lower().endswith(nen) for nen in cls.NON_EXECUTABLE_EXTENTIONS)
        ]
        if len(executables) != 1:
            raise RuntimeError(f"Couldn't automatically identify executable.\nCandidates: {executables}")
        
        cls.executable = os.path.join(this_dir_name, executables[0])


    @classmethod
    def tearDownClass(cls):
        '''
        Perform any necessary teardown of the program being tested here.
        '''
        test_names = cls.find_test_names() # refers to superclass
        findmodules.make_vpl_evaluate_cases(cls.SUBCLASS_FILE, globals(), include_pylint=False)
        return super().tearDownClass()


    @classmethod
    def getExecutable(cls):
        return cls.executable


    def run_program(self, cli_args: list[str], input_string: str):
        return subprocess.run([self.executable] + cli_args, input=input_string, **self.SUBPROCESS_RUN_OPTIONS)
    
    @classmethod
    def find_test_names(cls):
        return unittest.getTestCaseNames(cls, unittest.loader.TestLoader.testMethodPrefix)