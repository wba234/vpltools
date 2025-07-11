import unittest
import vpltools
import warnings

import vpltools.vpl_test_case

__unittest = True

class test_multi_class_java_package(vpltools.VPLTestCase):
    key_source_files = []
    ignore_files = []
    make_vpl_evaluate_cases_file = False

    dogstacker_output = (
          "Dog{name='Emperor Slobberface', dateOfBirth='2021-04-05', tricks=[Spin]}\n"
        + "Dog{name='Sir Barksalot', dateOfBirth='2017-09-12', tricks=[Jump]}\n"
        + "Dog{name='Duke Wigglebottom', dateOfBirth='2020-01-30', tricks=[Play Dead, Shake Paw]}\n"
        + "Dog{name='Baron von Drool', dateOfBirth='2019-07-15', tricks=[Fetch]}\n"
        + "Dog{name='Lord Fluffington', dateOfBirth='2018-05-21', tricks=[Sit, Roll Over]}\n"
    )

    @classmethod
    def setUpClass(cls):
        pass # Override the class setup, so that we can call this manually later. 
    
    
    @unittest.expectedFailure
    def test_dogstacker_package_compilation(self):
        self.set_this_dir_name()

        if self.key_source_files is None:
            warnings.warn("key_source_files unspecified! Assuming no key program. \nInitialize this class attribute to an empty list to silence this warning.")
            self.key_source_files = []

        try:
            self.student_program = self.compile_student_program()
        except vpltools.vpl_test_case.UnsupportedFeatureError:
            self.fail("Java packages are not supported.")

        student_process = self.run_student_program([], input_string="")
        self.assertEqual(student_process.stdout, self.dogstacker_output)

        
if __name__ == "__main__":
    unittest.main()
