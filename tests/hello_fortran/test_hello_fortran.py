import vpltools

__unittest = True

class TestHelloFortran(vpltools.VPLTestCase):
    '''
    Tests compilation of a basic Fortran 90 program.
    '''
    key_source_files = []
    ignore_files = []

    def test_hello_fortran(self):
        '''
        Tests if the program prints hello world.
        '''
        student_process = self.run_student_program([], input_string="")
        self.assertEqual(student_process.stdout, "Hello World!\n")

if __name__ == "__main__":
    vpltools.main()
