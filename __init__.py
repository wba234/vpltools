from findmodules import *
# # "This page intentionally left blank".
# # from findmodules import *

# # findmodule.py -- William Bailey -- 19 May 2023.
# '''
# A module for automatic discovery of student submission files in the 
# current working directory. Intend for use with Moodle VPL activities.
# '''
# import importlib
# import os
# import warnings
# # import regex
# # ^^ This could probably be done better with regular expressions

# def find_all_modules_in_dir(use_directory, remove_tests=True, verbose=False, s_extension=".py"):
#     '''
#     Returns a list of the names of all files in use_directory which end with ".py".
#     If remove_tests is True, those which begin with "test" will be removed from the list.
#     If verbose is True, the entire list, removed items, and kept items will be printed.
#     '''
#     module_list : list = os.listdir(use_directory) 
    
#     if verbose:
#         print(module_list)

#     i = 0
#     while i < len(module_list):
#         if module_list[i][-1*len(s_extension):] != s_extension:
#             if verbose:
#                 print("Deleting", module_list[i])
#             del module_list[i]
#         else:
#             i += 1

#     if verbose:
#         print(module_list)

#     if remove_tests:
#         i = 0
#         while i < len(module_list):
#             if module_list[i][:4] == "test":
#                 module_list.remove(module_list[i])
#             else:
#                 i += 1
#     if verbose:
#         print(module_list)

#     return module_list

    
# def import_student_module(use_directory, ignore_when_testing=[None], module_extension=".py"):
#     '''
#     Searches the local directory for files ending in module_extension. 
#     Ignores module_to_test, and things starting with "test".
#     ignore_when_testing can be a string, or a list of strings, with our without the module_extension.
#     '''

#     modules = find_all_modules_in_dir(use_directory, remove_tests=True)

#     # If it's a string, put it into a list.
#     if isinstance(ignore_when_testing, str):
#         ignore_when_testing = [ignore_when_testing]

#     # Then loop over the list, as if it had been a list the whole time. Because it might have been.
#     for ignored_module in ignore_when_testing:
#         if ignored_module is None:
#             continue
        
#         # Add the module extension if it's not already there.
#         if ignored_module[-len(module_extension):] != module_extension:
#             ignored_module += module_extension

#         # Remove the module, unless it's not there, in which case, warn about it.
#         try:
#             modules.remove(ignored_module)
#         except ValueError:
#             warnings.warn(f"Module '{ignored_module}' not found, not ignored.", RuntimeWarning)

#     if len(modules) > 1:
#         raise ImportError(f"More than one file found: {modules}. Exiting...")

#     if len(modules) < 1:
#         raise ImportError(f"No other python files found! Exiting...")
#     module = modules[0][:-1*len(module_extension)]

#     return importlib.import_module(module)


# def main():
#     print(find_all_modules_in_dir(remove_tests=True))


# if __name__ == "__main__":
#     main()
