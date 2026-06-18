'''
REMEMBER:
- Test files should start with "test".
- Test methods should also start with "test".

To run tests, you can use the command
$ python3 -m unittest
'''

import vpltools

__unittest = True

class test_class_name(vpltools.RegexTestCase):
    '''
    RegexTestCases objects test the functionality of a regular expression expressed as 
    the return value of a Python function. They should be raw strings, generally. E.g.,
    
    def exercise1():
        return r"[0-9]*

    RegexTestCase will find python files automatically, and import them, so you can 
    invoke their methods, and retrieve the regex, to pass to match_text(), or 
    match_and_capture_text().
    '''
    # key_source_files = []
    # ignore_files = []

    def test_match_method_name(self):
        inst = vpltools.MatchTarget("3.14159")
        self.match_text(self.student_py_module.exerciseN(), inst)
    
    def test_capture_method_name(self):
        inst = vpltools.MatchTarget("file://localhost:4040/zip_file", None, "localhost")
        self.match_and_capture_text(self.student_py_module.exerciseN(), inst) 


if __name__ == "__main__":
    vpltools.main()
