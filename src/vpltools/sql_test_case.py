from typing import Type
# import mariadb
import unittest
import os.path
import sqlite3 as sl
from itertools import permutations
from enum import Enum
import pandas as pd
import vpltools

__unittest = True
class InMemoryTestingDatabase:
    '''
    An object representing an ephemeral SQLite 3 database.
    setup_script_name : string representing an SQL script which builds a database.
    '''
    def __init__(self, setup_script_name: str):
        self.connection = sl.connect(":memory:")
        with open(setup_script_name, 'r') as fo:
            script_contents = fo.read()
            
        self.cursor = self.connection.executescript(script_contents)


    def getConnection(self) -> sl.Connection:
        return self.connection

class SupportedSQLBackends(Enum):
    MariaDB = 'mariadb'
    SQLite3 = 'sqlite3'

# class TestSQLQuery(unittest.TestCase): #, abc.ABC):
class TestSQLQuery(vpltools.VPLTestCase):
    '''
    A TestCase class meant to be subclassed. Provides the setup and teardown
    methods which open close connections to the database.
    '''

    # Users overriding this class, i.e., actually writing test for student code, should 
    # give these values in their subclasses.
    use_database: Type[InMemoryTestingDatabase] | None = None

    backend: SupportedSQLBackends = SupportedSQLBackends.SQLite3

    # conn : mariadb.Connection = None
    conn : sl.Connection

    # Greater abstraction may be required if multiple backends are to be supported.
    # For the moment, 
    @classmethod
    def setUpClass(cls): # type: ignore
        '''
        Called before any test in the class is run. Sets the self.conn attribute to 
        a valid database connection, ready for queries to be submitted.
        '''
        if cls.use_database is None:
            raise ValueError("Cannot execute query - no database specified!")

        if cls.backend == SupportedSQLBackends.SQLite3:
            rrc_db = cls.use_database() # type: ignore
            conn = rrc_db.getConnection()
            cls.conn = conn
        elif cls.backend == SupportedSQLBackends.MariaDB:
            raise NotImplementedError
        else:
            raise ValueError(f"RDBMS backend '{cls.backend}' is not supported. Choose between {list(SupportedSQLBackends)}.")

        super().setUpClass()



class TestSQLSelectQuery(TestSQLQuery):
    '''
    A TestCase class meant to test that the output of two SELECT
    queries are the same. Allows comparing records in order, or 
    out of order, and allows matching of aliased columns by ensuring 
    that all the data in each column is the same.
    '''
    @staticmethod
    def inexplicablyNonstandardEquals(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
        '''
        pd.DataFrame.equals() did not have the behavior I expected. I expected:
        
        Returns True if df1 and df2 have identically-named columns and indexed rows 
        (raises ValueError if they do not), and identical values in each location.
        '''
        return all((df1 == df2).all())


    def compareQueries(self, key_file_name: str, lab_file_name: str, file_dir: str, record_order_does_matter: bool = False) -> None:
        '''
        Helper function for testing the output of SELECT queries. 
        
        Raises AssertionError
        if the data sets returned by the queries in file_dir/key_file_name and 
        file_dir/lab_file_name are not identical. The notion of identical permits record
        order to differ. Pass record_order_does_matter=True to change this behavior.
        The order and names of columns never matters.
        '''
        # TODO: This could use some formal test cases.
        key_file_path = os.path.join(file_dir, key_file_name)
        lab_file_path = os.path.join(file_dir, lab_file_name)

        # Read the contents of files which contain queries.
        with open(key_file_path, 'r') as key_fo:
            key_df = pd.read_sql_query(key_fo.read(), self.conn)

        with open(lab_file_path, 'r') as lab_fo:
            lab_df = pd.read_sql_query(lab_fo.read(), self.conn)

        # Do we have the correct shape?
        self.assertEqual(
            key_df.shape, 
            lab_df.shape, 
            msg=f"Expected {key_df.shape[0]} rows, {key_df.shape[1]} columns, "
              + f"received {lab_df.shape[0]} rows, {lab_df.shape[1]} columns.")

        # The columns might be out of order. Check by finding all shared columns.
        key_columns = set(key_df.columns)
        lab_columns = set(lab_df.columns)

        shared_columns = list(key_columns.intersection(lab_columns))

        unmatched_key_columns = list(key_columns.difference(shared_columns))
        unmatched_lab_columns = list(lab_columns.difference(shared_columns))
        
        key_resolution_candidate = key_df[shared_columns + unmatched_key_columns]
        if not record_order_does_matter:
            key_resolution_candidate = key_resolution_candidate.sort_values(list(key_resolution_candidate.columns))
            key_resolution_candidate = key_resolution_candidate.reset_index(drop=True)
        

        # BTW: This can't be rolled into the loop below, because if all the 
        # columns match, then there are 0 permutations, and the loop doesn't 
        # run. So we need to check it here.
        if len(unmatched_key_columns) == 0 and len(unmatched_lab_columns) == 0:
            lab_resolution_candidate = lab_df[shared_columns]
            if not record_order_does_matter:
                lab_resolution_candidate = lab_resolution_candidate.sort_values(list(lab_resolution_candidate.columns))
                lab_resolution_candidate = lab_resolution_candidate.reset_index(drop=True)

                self.inexplicablyNonstandardEquals(key_resolution_candidate, lab_resolution_candidate)

                msg=(f"The columns were correct, but the data was not.\n"
                    +f"Expected:\n{key_df}\n\nReceived:\n{lab_df}")
                return  # Could keep going, but no need. Test passes.
            

        for perm in permutations(unmatched_lab_columns):
            lab_resolution_candidate = lab_df[shared_columns + list(perm)]
            lab_resolution_candidate = lab_resolution_candidate.rename(columns=dict(zip(lab_resolution_candidate.columns, key_resolution_candidate.columns)))
            if not record_order_does_matter:
                lab_resolution_candidate = lab_resolution_candidate.sort_values(list(lab_resolution_candidate.columns))
                lab_resolution_candidate = lab_resolution_candidate.reset_index(drop=True)

            try:
                self.assertTrue(self.inexplicablyNonstandardEquals(key_resolution_candidate, lab_resolution_candidate))
                print("Column Alignment:")
                print(f"KEY: {list(key_resolution_candidate.columns)}")
                print(f"LAB: {shared_columns + list(perm)} ")
                return # Columns aligned, test passed.
            
            except AssertionError:
                pass

        self.fail(f"Queries did not produce the same data sets!\nExpected:\n{key_df}\n\nGot:\n{lab_df}")



if __name__ == "__main__":
    unittest.main()
