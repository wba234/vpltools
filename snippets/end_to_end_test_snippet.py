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
    Tests the functionality of a non-Python program.
    '''
    key_source_files = []
    ignore_files = []

    def test_method_name(self):
        '''
        Describe any peculiarities of the program being tested here.
        '''
        student_process = self.run_student_program([], input_string="")
        self.assertEqual(student_process.stdout, "Hello World!")


if __name__ == "__main__":
    vpltools.main()
