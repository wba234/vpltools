import unittest
import vpltools

__unittest = True

class TestOwnerNames(vpltools.TestSQLSelectQuery):
    key_source_files = [ "key_all_owners.sql" ]
    
    use_database = "red_river_climbs_sqlite.sql"
    backend = vpltools.SupportedSQLBackends.SQLite3

    permit_select_all = False
    permit_natural_join = False

    ignore_files = [
        "red_river_climbs_sqlite.sql",
        "red_river_climbs_mariadb.sql",
        "make_sqlite_version.py",
        "RunRedRiverClimbsDB.py"
    ]

    def testSelectAllOwners(self):
        self.assertQueryOutputsEqual()

if __name__ == "__main__":
    unittest.main()
        