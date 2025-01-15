'''
REMEMBER:
- TEST FILES SHOULD START WITH "test"
- TEST METHODS SHOULD START WITH "test"
To run tests, you can use the command
$ python3 -m unittest discover # the discover is optional.
$ python3 <test_module_name>
'''

import unittest
import vpltools

__unittest = True

class test_class_name(vpltools.VPLTestCase):
    '''
    Describe any peculiarities of the program being tested here.
    '''
    key_source_files = []
    ignore_files = []

    def test_function_name(self):
        '''
        Describe any peculiarities of the function being tested here.
        '''
        # Go for it...
        # Use self.student_py_module, self.key_py_module to access python functions directly
        # Use self.run_student_program, self.run_key_program to run programs in subprocesses.
        student_process = self.run_student_program([], input_string="")
        self.assertEqual(student_process.stdout, "Hello World!\n")
        
if __name__ == "__main__":
    unittest.main()
