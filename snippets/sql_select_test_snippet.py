'''
REMEMBER:
- Test files should start with "test".
- Test methods should also start with "test".

To run tests, you can use the command
$ python3 -m unittest
'''

import vpltools

__unittest = True

class test_class_name(vpltools.TestSQLSelectQuery):
    key_source_files = [ "correct_query.sql" ]

    use_database = "db_init_file.sql"
    backend = vpltools.SupportedSQLBackends.SQLite3

    permit_select_all = False
    permit_natural_join = False

    ignore_files = []

    def test_method_name(self):
        self.assertQueryOutputsEqual()

if __name__ == "__main__":
    vpltools.main()
