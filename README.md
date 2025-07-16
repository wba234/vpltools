# About VPLTools
VPLTools is a package for writing tests which work with the VPL Moodle plugin. Test code is--naturally--written in Python, but VPLTools enables end-to-end testing of programs written in other languages too.

## Key Features
VPLTools seeks to make implementing VPL assignments as easy as possible. Most of its features are available as part of the ```VPLTestCase``` class, which should be extended to create tests, like your would with Python's ```unittest.TestCase```. The ```VPLTestCase``` class provides a number of features:
- automatic detection, and when necessary, compilation of student files. This means that you can write end-to-end tests which allow students to use any programming language supported by VPLTools.
- automatic importing of key and student Python programs as modules
- automatic generation the ```vpl_evaluate.cases``` file

## Usage
### Directory Setup
It is recommended that you use a separate directory for each assignment and its associated tests. A typical directory structure might look like this:
```text
temperature_conversion_lab
├── assignment_description.html
├── temp_conversion_starter_code.py
├── test_f2c.py
├── f2c_key.py
├── buggy_f2c.py
└── vpl_evaluate.cases
```
- ```assignment_description.html``` is the assignment prompt for students
- ```temp_conversion_starter_code.py``` is code for students to build on
- ```test_f2c.py``` contains the ```vpltools.VPLTestCase``` which implements the tests
- ```f2c_key.py``` is the instructor's solution
- ```buggy_f2c.py``` is a simulated student submission, to run the tests on
- ```vpl_evaluate.cases``` is the file describing which tests the VPL plugin should run

**When posting a VPL assignment**, remember to upload:
- the test file
- the key program, if required by the test file
- ```vpl_evaluate.cases```

You also need to enable the ***keep files when running*** option for each of these.

### Writing Tests
Test file names should start with "test_" and be located in the same directory as your answer key program, and any simulated student submissions to run the tests on. Write tests as your normally would with Python's ```unittest``` module. The ```vpl_evaluate.cases``` file is generated automatically (in ```tearDownClass```) when the set of test cases runs to completion. 

In addition to the features of the ```unittest``` package, you can use the following attributes and functions provided by ```VPLTestCase```:
   #### Important Methods
   - ```run_student_program()``` - Call this to execute the student's program in a subprocess.
   - ```run_key_program()``` - Call this to execute the solution program in a subprocess.

   #### Important Attributes
   - ```key_source_files: list[str]``` - Set this in class scope to tell VPLTools which files in the local directory are part of the solution program. Can be empty.
   - ```ignore_files: list[str]``` - Set this in class scope to tell VPLTools which files in the local directory should be ignored.
   - ```permitted_student_languages: list[SupportedLanguage]``` - Set this to restrict which programming languages are permitted. ```NoProgramError``` will be thrown if this is violated. Set to ```vpltools.SUPPORTED_LANGUAGES``` by default. Currently, the following languages are supported; use the strings below as keys in the ```SUPPORTED_LANGUAGES``` dictionary to refer to them when constructing your ```permitted_student_languages```. E.g., if you only want to allow C++, set ```permitted_student_languages = [ SUPPORTED_LANGUAGES["C++] ]```:
        - ```"C"```
        - ```"CPP"```
        - ```"JAVA"```
        - ```"PYTHON"```
        - ```"SQL"```

   - ```student_py_module: ModuleType | None``` - Use this to access student functions directly (Python submissions only).
   - ```key_py_module: ModuleType | None``` - Use this to access solution program functions directly (Python solutions only).
   - ```student_outfile_name: str``` - Predefined name for student output files. This must be passed as an argument to student programs when invoking them with ```run_student_program()```. This means that student programs must accept the name of an output file as one of their program's inputs.
   - ```key_outfile_name: str:``` - Predefined name for solution program output files.
   - ```run_basic_tests: list[function]``` - Define a list of basic tests from ```vpltools.basic_tests.BASIC_TESTS``` to run when importing student Python programs. This list is empty by default.
   - ```include_pylint: bool``` - Flag to include a VPL case which runs the PyLint static analyzer on student's submission, and passes only if PyLint is completely happy (Python only).


## Example Usage - Python Unit Testing
```python
import unittest
import vpltools

__unittest = True # Silence tracebacks from this module.

class TestF2C(vpltools.VPLTestCase):
    key_source_files = [ "f2c_key.py", ]
    ignore_files = [ "temp_conversion_starter_code.py", ]

    def mainAssertLogic(self, temp):
        stuTemp = self.student_py_module.fahrenheit_to_celsius(temp)
        keyTemp = self.key_py_module.fahrenheit_to_celsius(temp)
        self.assertAlmostEqual(
            stuTemp,
            keyTemp,
            places=4,
            msg=f'{temp}F should be {keyTemp}C, not {stuTemp}C.')

    def testFreezingPoint(self):
        freezingTempF = 32.0
        self.mainAssertLogic(freezingTempF)
    
    def testBoilingPoint(self):
        boilingTempF = 212.0
        self.mainAssertLogic(boilingTempF)

if __name__ == '__main__':
    unittest.main()
```

Note that ```__unittest = True``` has the effect of suppressing parts of error tracebacks which originate from within testing code, and which can be confusing to students.

### Example Use - End-to-End Testing
```python
import os.path
import unittest
from subprocess import TimeoutExpired
from findmodules import VPLTestCase

class TestBruteForceKnapsack(VPLTestCase):
    '''
    Run a program which produces an outfile with all the possible selections 
    for a Knapsack problem. Compare the outputs to ensure that all possibilities 
    have been tested, and the optimal has been found.
    '''
    # keySourceFiles = [ "key_brute_force_knapsack.py", ]
    keySourceFiles = [ "key_brute_force_knapsack.c", ]

    input_file_names = [
        "knapsack_input1.txt",
        "knapsack_input2.txt",
    ]

    @staticmethod
    def parse_output_file(file_name: str) -> list[tuple]:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(file_path, "r") as fo:
            options_list = []
            while bitstring := fo.readline().strip():
                options_list.append((bitstring, int(fo.readline()), int(fo.readline())))
        
        return options_list
    
    def test_4items_70kg_file1(self):
        self.run_and_compare_output_files("4", "70", self.input_file_names[0])

    def run_and_compare_output_files(self, max_items, max_weight, input_file):
        '''
        This is the main logic of the test cases. 
        It runs both programs, and compares the output files.
        '''
        more_subprocess_run_options = {
            "timeout" : 30
        }

        # Run both programs with the same commands, except for the output_file.
         lab_proc = self.run_student_program(
               [max_items, max_weight, input_file, self.student_outfile_name], 
               input_string="",
               **more_subprocess_run_options)

         key_proc = self.run_key_program(
               [max_items, max_weight, input_file, self.key_outfile_name], 
               input_string="",
               **more_subprocess_run_options)

        # Read the created files...
        lab_output = self.parse_output_file(self.student_outfile_name)
        key_output = self.parse_output_file(self.key_outfile_name)

        # ...compare the optimal solutions...
        self.assertTupleEqual(
            lab_output[-1][1:], 
            key_output[-1][1:], 
            msg=(
                f"With {max_items} items from {input_file}, and a limit of {max_weight}kg,\n"
                + f"the selected items should be {key_output[-1][0]} not {lab_output[-1][0]}."))
        
        # ...and the list of all possible options.
        sorted_lab_output = sorted(lab_output[:-1], key=lambda tpl: tpl[0])
        sorted_key_output = sorted(key_output[:-1], key=lambda tpl: tpl[0])
        
        self.assertListEqual(
            sorted_lab_output,
            sorted_key_output,
            msg=(
                "Your list of possibilities was not correct.\n"
                + "Please double-check:\n"
                + "\t- The number of 3-line blocks, and\n"
                + "\t- the order of lines in each 3-line block.\n"))

if __name__ == "__main__":
    unittest.main()
```

## Other Programming Assignments
In addition to ```VPLTestCase``` VPLTools also provides some classes which support other, more specific types of programming assignments:
 - ```HistorySearcher``` for command-line tutorial assignments which ask students to submit a list of their command history.
- ```RegexTestCase``` for assignments which ask students to submit a regular expression pattern.

## VSCode Snippet
There is a snippet for this boilerplate in ```/.vscode```. The format of the snippet (JSON) is a little specific to VSCode, but the code can be extracted relatively easily. Type ```test``` in a snakefile to trigger the snippet. 

# To Do
- Add snippets for SQL tests.
- Add snippets for other language End-to-end tests.
- Add snippets for regex tests.
- Test this under Windows? VPLJail is a POSIX system, right? Do I need to worry about windows?
- Add instrumentation, so that submissions could be tracked and studied. You'll probably want a database for this, and to seek IRB approval before switching it on.
- What would it take to add support for detecting AI-generated code?
- Make Java packages work?
- Publish this to PPI?
- Add a method for writing student and key output files to memory mapped files, for speed.
- Add a method for writing each test output file from the key program to a separate file, so that they can be cached, for speed.

## Installation
To use this with Moodle VPLs, you will need to install this package into your Moodle VPLJail manually. At time of writing, ```vpltools``` is _not_ in the Python Package Index. To install manually:
1. Download this repository.
2. Navigate (i.e. ```cd```) into the top-level folder of the repository. You should see a file called ```pyproject.toml```.
3. In a terminal, run ```python3 -m pip install .``` to install the program. If you are actively developing this module, you may want to install this in "editable" mode by adding ```-e``` or ```--editable```
```python3 -m pip install -editable .```. 
### Installing in VPLJail
You _should not_ install this in editable mode in the VPLJail. This will cause the package not to be found by the Python interpreter. Also, after installing anything into the VPLJail, you should restart the service with: ```systemctl restart vpl-jail-service```.

### Before Installing
This package requires the ```mariadb``` Python package. This means that there must be a functioning MariaDB installation, including the system packages ```libmariadb3``` ```libmariadb-dev```. So before installing ```vpltools```, run this command:
```bash
sudo apt install mariadb-server libmariadb3 libmariadb-dev
```

## Build Process
1. Navigate to top level directory.
2. Install ```build``` if necessary:
   ```bash
   python3 -m pip install --upgrade build
   ```

3. Build ```vpltools```:
   ```bash
   python3 -m build
   ```

4. Install ```vpltools``` in editable mode (in case you find bugs):
   ```bash
   python3 -m pip install --editable . # Note the period!
   ```

5. Check that the module is importable:
   Get out of the directory where the module actually lives. That'll cheat on the importing test:
   ```text
   $ python3
   >>> import vpltools
   ```


# Python packaging Tutorial Commands
This module was packaged by following and adapting to the [Python.org packaging tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/), around January 2024.
A summary of the commands used is below, along with the suggested directory structure:
```console
~/Documents/vpltools/
   |- tests/
   |- src/
   |  |- vpltools/
   |  |  `- example.py
   |  |  `- __init__.py
   `- license.txt
   `- readme.md
   `- pyproject.toml
```

The commands are fun from within the top-level module directory: ```~/Documents/vpltools/```
```bash
python3.10 -m pip install --upgrade build  # failed?
python3.10 -m build                        # failed to create virtual environment
sudo apt-install python3.10-venv           # OK with password
python3.10 -m build                        # Build succeeded
```

But usually, if everything is installed, you can just:
1. Make edits to the package.
2. Edit the version number in pyproject.toml (with ```vim pyproject.toml```)
3. Rebuild the package with ```$ python3.10 -m build```
4. Reinstall the package with ```$ python3.10 pip install . --editable``` (Of course, this shouldn't be necessary, but the version number won't change unless you do this.)
