# About VPLTools
VPLTools is a package for writing tests which work with the VPL Moodle plugin. Tests are obviously written in Python, but it enables easy end-to-end testing of programs written in other languages too.



## Typical Programming Assignments - ```VPLTestCase```
Chiefly, VPLTools provides ```VPLTestCase```, a subclass of Python's native ```unittest.TestCase```, with functionality specific to working with Moodle VPLs. By subclassing this, instructors can define tests for most types of programming assignments.

### Directory Setup
It is recommended that you use a separate directory for each assignment. A typical directory structure might look like this:
```text
temperature_conversion_lab
├── assignment_description.html
├── temp_conversion_starter_code.py
├── test_f2c.py
├── f2c_key.py
├── buggy_f2c.py
└── vpl_evaluate.cases
```
- ```assignment_description.html``` is the assignment prompt for students.
- ```temp_conversion_starter_code.py``` is code for students to build on.
- ```test_f2c.py``` contains the ```vpltools.VPLTestCase``` which implements the tests.
- ```f2c_key.py``` is the instructor's solution.
- ```buggy_f2c.py``` is a simulated student submission, to run the tests on.
- ```vpl_evaluate.cases``` is the file describing which tests the VPL plugin should run.

**When posting a VPL assignment**, remember to upload:
- the test file
- the key program, if referenced by the test file
- ```vpl_evaluate.cases```
You also need to enable the ***keep files when running*** option for each of these.


### Example Use - Python Unit Testing
```python
import unittest
import vpltools

__unittest = True

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

Things to note about this example:
- ```__unittest = True``` has the effect of suppressing parts of error tracebacks which originate from within testing code, and which can eb confusing to students.
- ```key_source_files``` is a list of files which constitute the instructors solution. They are ignored when searching for student's files.
- There are other important options which may be specified as class attributes in ```VPLTestCase``` subclasses. They are:
   - ```ignore_files``` - a list of files which should be ignored by vpltools. (e.g., starter code or alternative solutions)
   - ```skip_basic_tests``` - (Python submissions only) list of tests which should be skipped when importing student solutions. Basic tests are not run on Instructor solutions. To skip all basic tests, set this to ```vpltools.BASIC_TESTS```.
   - ```include_pylint``` - (Python submissions only) boolean flag indicating if a Pylint case should be added to the evaluate cases file.

### Example Use - End-to-End Testing


## Other Programming Assignments
In addition to ```VPLTestCase``` VPLTools also provides some classes which support other, more specific types of programming assignments:
 - ```HistorySearcher``` for command-line tutorial assignments which ask students to submit a list of their command history.
- ```RegexTestCase``` for assignments which ask students to submit a regular expression pattern.


## Important Attributes and Functions
- Write some notes about what new users should know:
   - that they need to set ```keySourceFiles```
   - that they can call ```run_student_program```
   - that they can call ```run_key_program```
   - that they can access ```student_py_module```
   - that they can access ```key_py_module```
   - that they can access output files.

# To Do
- Add a method for writing student and key output files to memory mapped files, for speed.
- Add a method for writing each test output file from the key program to a separate file, so that they can be cached, for speed.
- SQL Unittets need their 
    ```vpltools.make_vpl_evaluate_cases(__file__, locals(), include_pylint=False)``` at the bottom rolled into a ```tearDownClass``` method. This goes for all the various types of tests. NO BOILERPLATE.
- Add other basic tests?
- publish this to PPI?

# Snippet
You can use this exactly in your test files. **Note:** There is a snippet for this boilerplate in ```/.vscode```. The format of the snippet (JSON) is a little specific to VSCode, but the code can be extracted relatively easily. Type ```test``` in a snakefile to trigger the snippet. 

### Using Key Output Files instead of Re-running Key program each time.
This can speed up submission processing. See the ```VPLTestCase.use_pre_computed_key```.

## Installation
1. Download this repository.
2. Navigate (i.e. ```cd```) into the top-level folder of the repository. You should see a file called ```pyproject.toml```.
3. In a terminal, run ```python3 -m pip install .``` to install the program. You may want to install this in "editable" mode by adding ```-e``` or ```--editable```:
```python3 -m pip install --editable .```

__Note:__ To use this with Moodle VPLs, you will need to install this package into your Moodle VPLJail manually. At time of writing, ```vpltools``` is NOT in the Python Package Index.

## Build Process
1. Navigate to top level directory.
2. Install ```build``` if necessary:
   
   ```python3 -m pip install --upgrade build```

3. Build ```vpltools```:

   ```python3 -m build```

4. Install ```vpltools``` in editable mode (in case you find bugs):

   ```python3 -m pip install --editable .```

5. Check that the module is importable:

   ```cd ../``` Get out of the directory where the module actually lives. That'll cheat on the importing test.

   ```python3 -m vpltools```

   You should see a list of all the python modules you have in the directory where the command was run.

## Notes for Contributors:
- Consider installing this for each of your local Python 3 installations, e.g., CPython, and Anaconda. This may save a headache when the wrong one is invoked, and everything breaks unexpectedly.
- The directory structure is minimal. I had difficulty ensuring that the *package* was importable with ```import vpltools```rather than with ```from vpltools import vpltools``` or ```vpltools.vpltools```. If you know more about the packaging and distribution of Python projects than I do (it wouldn't take much) feel free to suggest a new organization.


# Python packaging Tutorial Commands
This module was packaged by following and adapting to the [Python.org packaging tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/), around January 2024.
A summary of the commands used is below, along with the suggested directory structure:
```
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
```
$ python3.10 -m pip install --upgrade build  # failed?
$ python3.10 -m build                        # failed to create virtual environment
$ sudo apt-install python3.10-venv           # OK with password
$ python3.10 -m build                        # Build succeeded
```

But usually, if everything is installed, you can just:
1. Make edits to the package.
2. Edit the version number in pyproject.toml (with ```vim pyproject.toml```)
3. Rebuild the package with ```$ python3.10 -m build```
4. Reinstall the package with ```$ python3.10 pip install . --editable``` (Of course, this shouldn't be necessary, but the version number won't change unless you do this.)
