import vpltools

class TestKeyProgramC(vpltools.VPLTestCase):
    '''
    Tests that files designated as key are ignored while compiling student programs,
    and vice versa. These programs don't do anyting.
    '''

    key_source_files = [ "key_program.c" ]

    def test_hello_c(self):
        '''
        Tests if the program prints hello world.
        '''
        student_process = self.run_student_program([], input_string="")
        self.assertEqual(student_process.stdout, "Hello World!\n")

    def test_programs_exist(self):
        '''
        Both a student and key program should exist at this point. 
        This test should never fail; if it would fail, cls.setUpClass()
        should have thrown an error, perhaps "multiple main() definition" or 
        "no such file or directory".
        '''
        self.assertIsNotNone(self.student_program, "Student program failed to compile.")
        self.assertIsNotNone(self.key_program, "Key program failed to compile.")

if __name__ == "__main__":
    vpltools.main()
