import vpltools

__unittest = True

class test_multi_class_java_program(vpltools.VPLTestCase):
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

    def test_dogstacker_compilation(self):
        student_process = self.run_student_program([], input_string="")
        self.assertEqual(student_process.stdout, self.dogstacker_output)
        # If this worked, then we compiled successfully.
        
if __name__ == "__main__":
    vpltools.main()
