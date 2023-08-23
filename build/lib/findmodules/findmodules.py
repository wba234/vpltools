# findmodule.py -- William Bailey -- 19 May 2023.
'''
A module for automatic discovery of student submission files in the 
current working directory. Intend for use with Moodle VPL activities.
'''
import importlib
import os
# import regex
# ^^ This could probably be done better with regular expressions

def find_all_modules_in_dir(remove_tests=True, verbose=False):
    s_extension = ".py"
    module_list = os.listdir() 
    
    if verbose:
        print(module_list)

    i = 0
    while i < len(module_list):
        if module_list[i][-1*len(s_extension):] != s_extension:
            if verbose:
                print("Deleting", module_list[i])
            del module_list[i]
        else:
            i += 1

    if verbose:
        print(module_list)

    if remove_tests:
        i = 0
        while i < len(module_list):
            if module_list[i][:4] == "test":
                module_list.remove(module_list[i])
            else:
                i += 1
    if verbose:
        print(module_list)

    return module_list

    
def import_student_module(ignore_module_to_test, module_extension=".py"):
    '''
    Searches the local directory for files ending in module_extension. 
    Ignores module_to_test, and things starting with "test".
    '''

    modules = find_all_modules_in_dir(remove_tests=True)
    modules.remove(ignore_module_to_test+module_extension)

    if len(modules) > 1:
        raise ImportError(f"More than one file found: {modules}. Exiting...")

    if len(modules) < 1:
        raise ImportError(f"No other python files found! Exiting...")
    module = modules[0][:-1*len(module_extension)]

    return importlib.import_module(module)


def main():
    print(find_all_modules_in_dir(remove_tests=True))


if __name__ == "__main__":
    main()
