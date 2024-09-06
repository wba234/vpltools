import unittest
import vpl_unittest

class TestMyProgram(vpl_unittest.VPLunittest):

    # def __init__(self, derived_class_location=__file__):
        # self.derived_class_location = derived_class_location

    def test_the_first(self):
        self.assertTrue(True)

    def test_the_second(self):
        self.assertTrue(False)

    def test_the_third(self):
        d = self.getTestNames() 
        # ^^ This works. Possibly only because it is called after 
        # all the functions are defined. But that's normal.

        # But how to get the location of the derived module?
        # Don't. Just pass it in as a path.
        
        print(self.derived_class_location)
        f = self.getFileModule()
        self.assertTrue(1)


if __name__ == "__main__":
    unittest.main()
