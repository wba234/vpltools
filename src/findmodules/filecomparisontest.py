import os

import findmodules

# class 

# class VPLProgramTester:
# class FileComparisonTest(findmodules.OpaqueTest):

    # pass

    # def __init__(self, 
    #              local_path_prefix: str, 
    #              test_cases: list[findmodules.VPLTestCase] = []):
    #     self.local_path_prefix = local_path_prefix
    #     self.test_cases = test_cases
    
    
    # def setUp(self):
    #     '''
    #     Cache a list all the files in the current working directory.
    #     '''
    #     self.this_dir_list_before = set(os.listdir(self.THIS_DIR_NAME))
    #     return super().setUp()


    # def tearDown(self):
    #     self.this_dir_list_after = set(os.listdir(self.THIS_DIR_NAME))
    #     new_files = self.this_dir_list_after.difference(self.this_dir_list_before)
    
    #     if len(new_files) == 1:
    #         self.most_recent_output_file = new_files[0]
    #     elif len(new_files > 1):
    #         raise RuntimeError("Only one output file is supported!")

    #     return super().tearDown()

    # def add_test_case(self, test_case):
    #     self.test_cases.append(test_case)


    # def make_vpl_evaluate_cases(self):
    #     print("Making vpl_evaluate.cases...", end="")
    #     case_blocks = ""
    #     for vpl_test_case in self.test_cases:
    #         case_blocks += vpl_test_case.make_all_case_blocks()

    #     write_to_file = "vpl_evaluate.cases"
    #     write_to_file = os.path.join(self.local_path_prefix, write_to_file)

    #     if not findmodules.overwrite_file_if_different(write_to_file, case_blocks, verbose=False):
    #         print("no changes...", end="")
        
    #     print("done.")