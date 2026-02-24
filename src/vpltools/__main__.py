import sys
import os
import vpltools.vpl_test_case

try:
    cwd = sys.argv[1]       # pre_vpl_run.sh should provide this
except:
    cwd = os.getenv("HOME") # if not, fall back to envionment

vpltools.vpl_test_case.VPLTestCase.key_source_files = []    # silences warning about unspecified key souce files.
vpltools.vpl_test_case.VPLTestCase.this_dir_name_override = cwd
vpltools.vpl_test_case.VPLTestCase.setUpClass()
vpltools.vpl_test_case.VPLTestCase.make_vpl_evaluate_cases()
