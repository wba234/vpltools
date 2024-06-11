import unittest
import os

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
    }

    @classmethod
    def setUpClass(cls):
        '''
        Perform any needed setup before all classes.
        '''
        this_dir_name = os.path.dirname(os.path.abspath(__file__))
        executables = [ 
            file_name for file_name in os.listdir(this_dir_name) 
            if not any(file_name.lower().endswith(nen) for nen in cls.NON_EXECUTABLE_EXTENTIONS)
        ]
        if len(executables) != 1:
            raise RuntimeError(f"Couldn't automatically identify executable.\nCandidates: {executables}")
        
        cls.executable = os.path.join(this_dir_name, executables[0])

    @classmethod
    def getExecutable(cls):
        return cls.executable
    