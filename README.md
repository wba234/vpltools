# Automatic Module Discovery
A module called ```findmodules``` which facilitates use of the Moodle VPLs by searching the current working directory for files which may be student work. There is also a feature which can generate ```vpl_evaluate.cases``` files automatically. This has the advantage of showing individual tests on the VPL web page, instead of one big test. The hope is that this makes debugging more approachable. See examples below for how to do this.

# TODO
-  Add a basic test ensuring that there are no global variables!

## Example Usages
1. Minimal Use. Find student's file, and run tests.
```
import os.path
import findmodules

lab = findmodules.import_student_module(os.path.dirname(__file__))
```

2. More involved: compare a student's code against known good code which serves as an answer key. I recommend that this be combined with number 3, below.
```
import os.path
import importlib
import findmodules
MODULE_TO_TEST = "fairground_ride_key"     # name of key file, which is ignored.

key = importlib.import_module(MODULE_TO_TEST)
lab = findmodules.import_student_module(os.path.dirname(__file__), ignore_when_testing=[MODULE_TO_TEST])
```

3. Make ```vpl_evaluate.cases```, to show tests individually in the Moodle assignment. I recommend that this approach be combined with number 2 above.
```
import findmodules
import unittest

class MyTestCaseClass(unittest.TestCase):

   # ...your TestCase here...

   @classmethod
   def tearDownClass(cls) -> None:
      findmodules.make_vpl_evaluate_cases(
         __file__, 
         globals(), 
         include_pylint=False)  
  
      return super().tearDownClass()

if __name__ == "__main__":
    unittest.main()
```
You can use this exactly in your test files. **Note:** There is a snippet for this boilerplate in the ```baileycs1``` repository, under ```/.vscode```. The format of the snippet (JSON) is a little specific to VSCode, but the code can be extracted relatively easily. Type ```test``` in a snakefile to trigger the snippet.

## Installation
1. Download this repository.
2. Navigate (i.e. ```cd```) into the top-level folder of the repository. You should see a file called ```pyproject.toml```.
3. In a terminal, run ```python3 -m pip install .``` to install the program. You may want to install this in "editable" mode by adding ```-e``` or ```--editable```:
```python3 -m pip install --editable .```

__Note:__ To use this with Moodle VPLs, you will need to upload this project's file ```findmodules.py``` along with the solution, test cases, and any other files. At time of writing, ```findmodules``` is NOT in the Python Package Index.

## Build Process
You you should not need to do this more than once, if at all.
1. Navigate to top level directory.
2. Install ```build``` if necessary:
   
   ```python3 -m pip install --upgrade build```

3. Build ```findmodules```:

   ```python3 -m build```

4. Install ```findmodules``` in editable mode (in case you find bugs):

   ```python3 -m pip install --editable .```

5. Check that the module is importable:

   ```cd ../``` Get out of the directory where the module actually lives. That'll cheat on the importing test.

   ```python3 -m findmodules```

   You should see a list of all the python modules you have in the directory where the command was run.

## Notes:
- Consider installing this for each of your local Python 3 installations, e.g., CPython, and Anaconda. This may save a headache when the wrong one is invoked, and everything breaks unexpectedly.
- The directory structure is minimal. I had difficulty ensuring that the *package* was importable with ```import findmodules```rather than with ```from findmodules import findmodules``` or ```findmodules.findmodules```. If you know more about the packaging and distribution of Python projects than I do (it wouldn't take much) feel free to suggest a new organization.


# Python packaging Tutorial Commands
This module was packaged by following and adapting to the [Python.org packaging tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/), around January 2024.
A summary of the commands used is below, along with the suggested directory structure:
```
~/Documents/findmodules/
   |- tests/
   |- src/
   |  |- findmodules/
   |  |  |- example.py
   |  |  |- __init__.py
   |- license.txt
   |- readme.md
   |- pyproject.toml
```

The commands are fun from within the top-level module directory: ```~/Documents/findmodules/```
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
