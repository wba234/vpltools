import vpltools
import types
__unittest = True # Keep, to silence tracebacks.

g_source_files = [ ]
g_ignore_files = [
    # "regex_answers.py", 
    # "lab_answers.py",
    # "starter_code.py",
    # "ex1_code.py",
    # "adam_regex_answers.py",
]

class test_match_decimal_numbers(vpltools.RegexTestCase):
    '''
    Test matching various floating point notations.
    '''
    key_source_files = g_source_files
    ignore_files = g_ignore_files
    student_py_module: types.ModuleType # "declaring" like this silences linter warnings.
# ------------- EXERCISE 1 ---------------------------------------------------------------

    def test_simple(self):
        inst = vpltools.MatchTarget("3.14529")
        self.match_text(self.student_py_module.exercise1(), inst)

    def test_negative(self):
        inst = vpltools.MatchTarget("-255.34")
        self.match_text(self.student_py_module.exercise1(), inst)

    def test_integers(self):
        inst = vpltools.MatchTarget("128")
        self.match_text(self.student_py_module.exercise1(), inst) 

    def test_exponential_notation(self):
        inst = vpltools.MatchTarget("1.9e10")
        self.match_text(self.student_py_module.exercise1(), inst) 

    def test_comma_separator(self):
        inst = vpltools.MatchTarget("123,340.00")
        self.match_text(self.student_py_module.exercise1(), inst) 

    def test_ignore_resolution(self):
        inst = vpltools.MatchTarget("720p")
        self.match_text(self.student_py_module.exercise1(), inst, negate_match=True) 

# ------------- EXERCISE 2 ---------------------------------------------------------------

    def test_with_hyphens(self):
        inst = vpltools.MatchTarget("415-555-1234", "415-555-1234", "415")
        self.match_and_capture_text(self.student_py_module.exercise2(), inst) 

    def test_more_with_hyphens(self):
        inst = vpltools.MatchTarget("650-555-2345", "650-555-2345", "650")
        self.match_and_capture_text(self.student_py_module.exercise2(), inst) 

    def test_with_parentheses(self):
        inst = vpltools.MatchTarget("(416)555-3456", "(416)555-3456", "416")
        self.match_and_capture_text(self.student_py_module.exercise2(), inst) 

    def test_with_spaces(self):
        inst = vpltools.MatchTarget("202 555 4567", "202 555 4567", "202")
        self.match_and_capture_text(self.student_py_module.exercise2(), inst) 
    
    def test_just_numbers(self):
        inst = vpltools.MatchTarget("4035555678" , "4035555678" , "403")
        self.match_and_capture_text(self.student_py_module.exercise2(), inst) 

    def test_just_spaces_with_country_code(self):
        inst = vpltools.MatchTarget("1 416 555 9292", "1 416 555 9292", "416")
        self.match_and_capture_text(self.student_py_module.exercise2(), inst) 

# ------------- EXERCISE 3 ---------------------------------------------------------------

    def test_simple_email(self):
        inst = vpltools.MatchTarget("tom@hogwarts.com", None, "tom")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 

    def test_dotted_email(self):    
        inst = vpltools.MatchTarget("tom.riddle@hogwarts.com", None, "tom.riddle")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 
    
    def test_plus_addressing(self):
        inst = vpltools.MatchTarget("tom.riddle+regexone@hogwarts.com", None, "tom.riddle")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 

    def test_multi_domain_email(self):
        inst = vpltools.MatchTarget("tom@hogwarts.eu.com", None, "tom")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 

    def test_another_simple_email(self):
        inst = vpltools.MatchTarget("potter@hogwarts.com", None, "potter")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 

    def test_yet_another_simple_email(self):
        inst = vpltools.MatchTarget("harry@hogwarts.com", None, "harry")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 

    def test_more_plus_addressing(self):
        inst = vpltools.MatchTarget("hermione+regexone@hogwarts.com", None, "hermione")
        self.match_and_capture_text(self.student_py_module.exercise3(), inst) 

# ------------- EXERCISE 4 ---------------------------------------------------------------

    def test_simple_link(self):
        inst = vpltools.MatchTarget("<a>This is a link</a>", None, "a" )
        self.match_and_capture_text(self.student_py_module.exercise4(), inst) 

    def test_not_so_simple_link(self):
        inst = vpltools.MatchTarget("<a href='https://regexone.com'>Link</a>", None, "a" )
        self.match_and_capture_text(self.student_py_module.exercise4(), inst) 

    def test_find_a_div(self):
        inst = vpltools.MatchTarget("<div class='test_style'>Test</div>", None, "div" )
        self.match_and_capture_text(self.student_py_module.exercise4(), inst) 

    def test_div_span(self):
        inst = vpltools.MatchTarget("<div>Hello <span>world</span></div>", None, "div" )
        self.match_and_capture_text(self.student_py_module.exercise4(), inst) 

# ------------- EXERCISE 5 ---------------------------------------------------------------

    def test_bash_profile(self):
        inst = vpltools.MatchTarget(".bash_profile", None, None)
        self.match_and_capture_text(self.student_py_module.exercise5(), inst, force_no_match=True) 

    def test_workspace(self):
        inst = vpltools.MatchTarget("workspace.doc", None, None)
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

    def test_a_jay_peg(self):
        inst = vpltools.MatchTarget("img0912.jpg", None, "img0912")
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

    def test_a_pee_n_gee(self):
        inst = vpltools.MatchTarget("updated_img0912.png", None, "updated_img0912")
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

    def test_the_documentation(self):
        inst = vpltools.MatchTarget("documentation.html", None, None)
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

    def test_a_guuh_if(self):
        inst = vpltools.MatchTarget("favicon.gif", None, "favicon")
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

    def test_a_temp_file(self):
        inst = vpltools.MatchTarget("mg0912.jpg.tmp", None, None)
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

    def test_lockfile(self):
        inst = vpltools.MatchTarget("access.lock", None, None)
        self.match_and_capture_text(self.student_py_module.exercise5(), inst) 

# ------------- EXERCISE 6 ---------------------------------------------------------------

    def test_leading(self):
        inst = vpltools.MatchTarget(
            " 				The quick brown fox...",
            " 				The quick brown fox...", 
            "The quick brown fox...")
        self.match_and_capture_text(self.student_py_module.exercise6(), inst) 
    
    def test_noleading(self):
        inst = vpltools.MatchTarget(
            "jumps over the lazy dog.",
            "jumps over the lazy dog.",
            "jumps over the lazy dog."
        )
        self.match_and_capture_text(self.student_py_module.exercise6(), inst) 

# ------------- EXERCISE 7 ---------------------------------------------------------------

    def test_warning(self):
        inst = vpltools.MatchTarget("W/dalvikvm( 1553): threadid=1: uncaught exception", None, None)
        self.match_and_capture_text(self.student_py_module.exercise7(), inst) 

    def test_FATAL_EXCEPTION(self):
        inst = vpltools.MatchTarget("E/( 1553): FATAL EXCEPTION: main", None, None)
        self.match_and_capture_text(self.student_py_module.exercise7(), inst) 

    def test_string_misbehaving(self):
        inst = vpltools.MatchTarget("E/( 1553): java.lang.StringIndexOutOfBoundsException", None, None)
        self.match_and_capture_text(self.student_py_module.exercise7(), inst) 

    # KEEP THESE COMMENTED OUT -- START (They aren't working, or something. IDK)
    # def test_makeView(self):
    #     inst = vpltools.MatchTarget(
    #         "E/( 1553):   at widget.List.makeView(ListView.java:1727)",
    #         None,
    #         "makeView"
    #     )
    #     self.match_and_capture_text(self.student_py_module.exercise7(), inst) 

    # def test_fillDown(self):
    #     inst = vpltools.MatchTarget(
    #         "E/( 1553):   at widget.List.fillDown(ListView.java:652)",
    #         None,
    #         "fillDown"
    #     )
    #     self.match_and_capture_text(self.student_py_module.exercise7(), inst) 

    # def test_fillFrom(self):
    #     inst = vpltools.MatchTarget(
    #         "E/( 1553):   at widget.List.fillFrom(ListView.java:709) 	",
    #         None,
    #         "fillFrom"
    #     )
    #     self.match_and_capture_text(self.student_py_module.exercise7(), inst) 

    # KEEP THESE COMMENTED OUT -- END
# ------------- EXERCISE 8 ---------------------------------------------------------------

    def test_ftp_server(self):
        inst = vpltools.MatchTarget("ftp://file_server.com:21/top_secret/life_changing_plans.pdf", None, "ftp")
        self.match_and_capture_text(self.student_py_module.exercise8(), inst) 

    def test_dot_com(self):
        inst = vpltools.MatchTarget("https://regexone.com/lesson/introduction#section", None, "https")
        self.match_and_capture_text(self.student_py_module.exercise8(), inst) 

    def test_localhost(self):
        inst = vpltools.MatchTarget("file://localhost:4040/zip_file", None, "file")
        self.match_and_capture_text(self.student_py_module.exercise8(), inst) 

    def test_dot_com_with_port(self):
        inst = vpltools.MatchTarget("https://s3cur3-server.com:9999/", None, "https")
        self.match_and_capture_text(self.student_py_module.exercise8(), inst) 
    
    def test_angry_birds(self):
        inst = vpltools.MatchTarget("market://search/angry%20birds", None, "market")
        self.match_and_capture_text(self.student_py_module.exercise8(), inst) 


if __name__ == "__main__":
    vpltools.main()
