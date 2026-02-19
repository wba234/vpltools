import vpltools

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

# ------------- EXERCISE 1 ---------------------------------------------------------------

    def test_simple(self):
        text_to_match = "3.14529"
        self.match_text(self.student_py_module.exercise1(), text_to_match)  # type: ignore

    def test_negative(self):
        text_to_match = "-255.34"
        self.match_text(self.student_py_module.exercise1(), text_to_match) # type: ignore

    def test_integers(self):
        text_to_match = "128"
        self.match_text(self.student_py_module.exercise1(), text_to_match) # type: ignore

    def test_exponential_notation(self):
        text_to_match = "1.9e10"
        self.match_text(self.student_py_module.exercise1(), text_to_match) # type: ignore

    def test_comma_separator(self):
        text_to_match = "123,340.00"
        self.match_text(self.student_py_module.exercise1(), text_to_match) # type: ignore

    def test_ignore_resolution(self):
        text_to_match = "720p"
        self.match_text(self.student_py_module.exercise1(), text_to_match, negate_match=True) # type: ignore

# ------------- EXERCISE 2 ---------------------------------------------------------------

    def test_with_hyphens(self):
        text_to_match_capture = {
            vpltools.RegexTestCase.TEXT : "415-555-1234",
            vpltools.RegexTestCase.FIND : "415-555-1234",
            vpltools.RegexTestCase.CAPT : "415",}
        self.match_and_capture_text(self.student_py_module.exercise2(), text_to_match_capture) # type: ignore

    def test_more_with_hyphens(self):
        text_to_match_capture = {
            vpltools.RegexTestCase.TEXT : "650-555-2345",
            vpltools.RegexTestCase.FIND : "650-555-2345",
            vpltools.RegexTestCase.CAPT : "650",}
        self.match_and_capture_text(self.student_py_module.exercise2(), text_to_match_capture) # type: ignore

    def test_with_parentheses(self):
        text_to_match_capture = {
            vpltools.RegexTestCase.TEXT : "(416)555-3456",
            vpltools.RegexTestCase.FIND : "(416)555-3456",
            vpltools.RegexTestCase.CAPT : "416",}
        self.match_and_capture_text(self.student_py_module.exercise2(), text_to_match_capture) # type: ignore

    def test_with_spaces(self):
        text_to_match_capture = {
            vpltools.RegexTestCase.TEXT : "202 555 4567",
            vpltools.RegexTestCase.FIND : "202 555 4567",
            vpltools.RegexTestCase.CAPT : "202",}
        self.match_and_capture_text(self.student_py_module.exercise2(), text_to_match_capture) # type: ignore
    
    def test_just_numbers(self):
        text_to_match_capture = {
            vpltools.RegexTestCase.TEXT : "4035555678", 
            vpltools.RegexTestCase.FIND : "4035555678", 
            vpltools.RegexTestCase.CAPT : "403",}
        self.match_and_capture_text(self.student_py_module.exercise2(), text_to_match_capture) # type: ignore

    def test_just_spaces_with_country_code(self):
        text_to_match_capture = {
            vpltools.RegexTestCase.TEXT : "1 416 555 9292",
            vpltools.RegexTestCase.FIND : "1 416 555 9292",
            vpltools.RegexTestCase.CAPT : "416",}
        self.match_and_capture_text(self.student_py_module.exercise2(), text_to_match_capture) # type: ignore

# ------------- EXERCISE 3 ---------------------------------------------------------------

    def test_simple_email(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "tom@hogwarts.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "tom"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore

    def test_dotted_email(self):    
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "tom.riddle@hogwarts.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "tom.riddle"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore
    
    def test_plus_addressing(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "tom.riddle+regexone@hogwarts.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "tom.riddle"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore

    def test_multi_domain_email(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "tom@hogwarts.eu.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "tom"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore

    def test_another_simple_email(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "potter@hogwarts.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "potter"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore

    def test_yet_another_simple_email(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "harry@hogwarts.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "harry"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore

    def test_more_plus_addressing(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "hermione+regexone@hogwarts.com",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "hermione"}
        self.match_and_capture_text(self.student_py_module.exercise3(), text_to_match_and_capture) # type: ignore

# ------------- EXERCISE 4 ---------------------------------------------------------------

    def test_simple_link(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "<a>This is a link</a>",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "a" }
        self.match_and_capture_text(self.student_py_module.exercise4(), text_to_match_and_capture) # type: ignore

    def test_not_so_simple_link(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "<a href='https://regexone.com'>Link</a>",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "a" }
        self.match_and_capture_text(self.student_py_module.exercise4(), text_to_match_and_capture) # type: ignore

    def test_find_a_div(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "<div class='test_style'>Test</div>",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "div" }
        self.match_and_capture_text(self.student_py_module.exercise4(), text_to_match_and_capture) # type: ignore

    def test_div_span(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "<div>Hello <span>world</span></div>",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "div" }
        self.match_and_capture_text(self.student_py_module.exercise4(), text_to_match_and_capture) # type: ignore

# ------------- EXERCISE 5 ---------------------------------------------------------------

    def test_bash_profile(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : ".bash_profile",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture, force_no_match=True) # type: ignore

    def test_workspace(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "workspace.doc",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

    def test_a_jay_peg(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "img0912.jpg",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "img0912",
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

    def test_a_pee_n_gee(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "updated_img0912.png",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "updated_img0912",
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

    def test_the_documentation(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "documentation.html",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

    def test_a_guuh_if(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "favicon.gif",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "favicon",
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

    def test_a_temp_file(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "mg0912.jpg.tmp",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

    def test_lockfile(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "access.lock",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise5(), text_to_match_and_capture) # type: ignore

# ------------- EXERCISE 6 ---------------------------------------------------------------

    def test_leading(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : " 				The quick brown fox...",
            vpltools.RegexTestCase.FIND : " 				The quick brown fox...",
            vpltools.RegexTestCase.CAPT : "The quick brown fox...",
        }
        self.match_and_capture_text(self.student_py_module.exercise6(), text_to_match_and_capture) # type: ignore
    
    def test_noleading(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "jumps over the lazy dog.",
            vpltools.RegexTestCase.FIND : "jumps over the lazy dog.",
            vpltools.RegexTestCase.CAPT : "jumps over the lazy dog.",
        }
        self.match_and_capture_text(self.student_py_module.exercise6(), text_to_match_and_capture) # type: ignore

# ------------- EXERCISE 7 ---------------------------------------------------------------

    def test_warning(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "W/dalvikvm( 1553): threadid=1: uncaught exception",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise7(), text_to_match_and_capture) # type: ignore

    def test_FATAL_EXCEPTION(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "E/( 1553): FATAL EXCEPTION: main",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise7(), text_to_match_and_capture) # type: ignore

    def test_string_misbehavin(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "E/( 1553): java.lang.StringIndexOutOfBoundsException",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : None,
        }
        self.match_and_capture_text(self.student_py_module.exercise7(), text_to_match_and_capture) # type: ignore

    # def test_makeView(self):
    #     text_to_match_and_capture = {
    #         vpltools.RegexTestCase.TEXT : "E/( 1553):   at widget.List.makeView(ListView.java:1727)",
    #         vpltools.RegexTestCase.FIND : None,
    #         vpltools.RegexTestCase.CAPT : "makeView",
    #     }
    #     self.match_and_capture_text(self.student_py_module.exercise7(), text_to_match_and_capture) # type: ignore

    # def test_fillDown(self):
    #     text_to_match_and_capture = {
    #         vpltools.RegexTestCase.TEXT : "E/( 1553):   at widget.List.fillDown(ListView.java:652)",
    #         vpltools.RegexTestCase.FIND : None,
    #         vpltools.RegexTestCase.CAPT : "fillDown",
    #     }
    #     self.match_and_capture_text(self.student_py_module.exercise7(), text_to_match_and_capture) # type: ignore

    # def test_fillFrom(self):
    #     text_to_match_and_capture = {
    #         vpltools.RegexTestCase.TEXT : "E/( 1553):   at widget.List.fillFrom(ListView.java:709) 	",
    #         vpltools.RegexTestCase.FIND : None,
    #         vpltools.RegexTestCase.CAPT : "fillFrom",
    #     }
    #     self.match_and_capture_text(self.student_py_module.exercise7(), text_to_match_and_capture) # type: ignore

# ------------- EXERCISE 8 ---------------------------------------------------------------

    def test_ftp_server(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "ftp://file_server.com:21/top_secret/life_changing_plans.pdf",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "ftp",
        }
        self.match_and_capture_text(self.student_py_module.exercise8(), text_to_match_and_capture) # type: ignore

    def test_dot_com(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "https://regexone.com/lesson/introduction#section",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "https",
        }
        self.match_and_capture_text(self.student_py_module.exercise8(), text_to_match_and_capture) # type: ignore

    def test_localhost(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "file://localhost:4040/zip_file",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "file",
        }
        self.match_and_capture_text(self.student_py_module.exercise8(), text_to_match_and_capture) # type: ignore

    def test_dot_com_with_port(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "https://s3cur3-server.com:9999/",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "https",
        }
        self.match_and_capture_text(self.student_py_module.exercise8(), text_to_match_and_capture) # type: ignore
    
    def test_angry_birds(self):
        text_to_match_and_capture = {
            vpltools.RegexTestCase.TEXT : "market://search/angry%20birds",
            vpltools.RegexTestCase.FIND : None,
            vpltools.RegexTestCase.CAPT : "market",
        }
        self.match_and_capture_text(self.student_py_module.exercise8(), text_to_match_and_capture) # type: ignore


if __name__ == "__main__":
    vpltools.main()
