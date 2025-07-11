import vpltools
import unittest

__unittest = True

class TestMaxDeveloperGrades(vpltools.TestSQLSelectQuery):
    key_source_files = [ "key_max_developer_grades.sql" ]
    
    use_database = "red_river_climbs_sqlite.sql"
    backend = vpltools.SupportedSQLBackends.SQLite3

    permit_select_all = False
    permit_natural_join = False
    ignore_files = [ "red_river_climbs_mariadb.sql", ]

    def testMaxDeveloperGrades(self):
        self.assertQueryOutputsEqual()

if __name__ == "__main__":
    unittest.main()