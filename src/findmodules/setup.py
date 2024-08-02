from distutils.core import setup

with open("README.md", "r") as fo:
    long_description = fo.read()

setup(name='findmodules',
      version='0.12',
      description=('Facilitates Moodle VPL use by searching the current '
                   +'working directory for other python files.'),
      long_description=long_description,
      author='William Bailey',
      author_email='william.bailey@centre.edu',
      url='https://github.com/wba234/baileycs1',
      package_dir={"":"src"},
      packages=['findmodules'],
     )