import unittest
import os
import subprocess
import findmodules
import sys

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


    @classmethod
    def setUpClass(cls):
        '''
        Perform any needed setup before all classes.
        '''
        cls.this_dir_name = os.path.dirname(sys.modules[cls.__module__].__file__)
        executables = [ 
            file_name for file_name in os.listdir(cls.this_dir_name) 
            if not any(file_name.lower().endswith(nen) for nen in cls.NON_EXECUTABLE_EXTENTIONS)
        ]
        if len(executables) != 1:
            raise RuntimeError(f"Couldn't automatically identify executable.\nCandidates: {executables}")
        
        cls.executable = os.path.join(cls.this_dir_name, executables[0])


    @classmethod
    def tearDownClass(cls):
        '''
        Find all names of unittest methods, and write them to a file in the same 
        directory as the subclass of this.
        '''
        test_names = unittest.getTestCaseNames(cls, unittest.loader.TestLoader.testMethodPrefix) # refers to subclass
        findmodules.make_cases_file(
            cls.this_dir_name, 
            { cls.__name__ : [test_method_name for test_method_name in test_names] },
            False
        )
        return super().tearDownClass()


    @classmethod
    def getExecutable(cls):
        return cls.executable


    @classmethod
    def run_program(self, cli_args: list[str], input_string: str):
        return subprocess.run([self.executable] + cli_args, input=input_string, **self.SUBPROCESS_RUN_OPTIONS)
