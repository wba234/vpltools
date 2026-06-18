'''
REMEMBER:
- Test files should start with "test".
- Test methods should also start with "test".

To run tests, you can use the command
$ python3 -m unittest
'''

import vpltools

__unittest = True

class test_class_name(vpltools.VPLTestCase):
    '''
    Describe any peculiarities of the program being tested here.
    '''
    key_source_files = ["key_program_source.ext"]
    ignore_files = []

    def test_function_name(self):
        '''
        Describe any peculiarities of the function being tested here.
        '''
        # Go for it...
        # Use self.student_py_module, self.key_py_module to access python functions directly
        # Use self.run_student_program, self.run_key_program to run programs in subprocesses.

if __name__ == "__main__":
    vpltools.main()
