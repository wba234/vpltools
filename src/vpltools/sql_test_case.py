# from typing import Type
import re
import sys
import abc
import os.path
import subprocess
import unittest
import sqlite3 as sl

import mariadb
import pandas as pd
from enum import Enum
from itertools import permutations

import vpltools

__unittest = True

class SupportedSQLBackends(Enum):
    MariaDB = 'mariadb'
    SQLite3 = 'sqlite3'



class Database(abc.ABC):
    '''
    An abstract base class representing a database which can be queried.
    Subclasses of this class require:
    1. a class attribute 'conn' to be defined. This should be an 
       _SQLConnection object, ideally, of the type supported by Pandas.
    2. a constructor accepting a the name of a script which will 
       be used to setup and populate the test database.
    2. a run_query() method. This should accepts a single string 
       of SQL code to be executed. The overridden method can use 
       the super() implementation, which uses Pandas' read_sql_query().
    '''
    conn = None 
    
    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError
    

    @abc.abstractmethod
    def run_query(self, query: str) -> pd.DataFrame:
        return pd.read_sql_query(query, self.conn)
    


class MariaDBPersistentDatabase(Database):
    '''
    An object representing a persistent MariaDB database.
    setup_script_name : string representing an SQL script 
    which builds a database.
    '''
    def __init__(self, setup_script_name: str, user: str, password: str, db_name: str):
        '''
        Sets up a MariaDB database by running setup_script_name, using
        the provided credentials. Note that the name of the database
        created by the script must match the provided db_name exactly.
        '''
        # The MariaDB connector does not support running scripts. 
        # So we run it in it's own process, command-line style.
        s = subprocess.run(["/usr/bin/mariadb", f"-u{user}", f"-p{password}", "-e", f"SOURCE {setup_script_name}"])

        if s.returncode != 0:
            raise RuntimeError("Couldn't initialize MariaDB database.\nPlease send the complete "
                               + "traceback from this error message to your instructor.")
        
        try:
            self.conn = mariadb.connect(
                user=user,
                password=password,
                host="localhost",
                database=db_name
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")
            sys.exit(1)

        self.cursor = self.conn.cursor()


    def run_query(self, query: str) -> pd.DataFrame:
        '''
        Executes query in the database represented by the calling object.
        '''
        return super().run_query(query)



class VPLDefaultDatabase(Database):
    '''
    An object representing VPL's default SQLite 3 database.
    VPL executes all .sql files automatically by default, so arguments are unused.
    '''
    default_db = "vpl.db"   # default name from VPL's default script (sql_run.sh).
    def __init__(self, test_file_dir: str):
        if not os.path.exists(os.path.join(test_file_dir, self.default_db)):
            raise FileNotFoundError # We're probably not running in the VPL jail

        self.conn = sl.connect(self.default_db)
        self.cursor = self.conn.cursor


    def run_query(self, query: str) -> pd.DataFrame:
        return super().run_query(query)
    


class InMemoryTestingDatabase(Database):
    '''
    An object representing an ephemeral SQLite 3 database.
    setup_script_name : string representing an SQL script which builds a database.
    '''
    def __init__(self, setup_script_name: str):
        self.conn = sl.connect(":memory:")
        with open(setup_script_name, 'r') as fo:
            script_contents = fo.read()
            
        self.cursor = self.conn.executescript(script_contents)


    def run_query(self, query: str) -> pd.DataFrame:
        '''
        Executes query in the database represented by the calling object.
        '''
        return super().run_query(query)



class TestSQLQuery(vpltools.VPLTestCase):
    '''
    A TestCase class meant to be subclassed. Provides the setup and teardown
    methods which open close connections to the database.

    Users overriding this class, i.e., actually writing test for student code, should 
    give these values in their subclasses:
    
    - use_database: str
    - backend: SupportedSQLBackends
    '''
    use_database: str = VPLDefaultDatabase.default_db
    backend: SupportedSQLBackends = SupportedSQLBackends.SQLite3

    conn : sl.Connection
    db : Database 
    db_name : str
    db_user : str
    db_password : str
    # Greater abstraction may be required if multiple backends are to be supported, e.g.:
    # conn : mariadb.Connection = None
    
    @classmethod
    def setUpClass(cls):
        '''
        Called before any test in the class is run. Sets the self.conn attribute to 
        a valid database connection, ready for queries to be submitted.
        '''
        cls.permitted_student_languages = [ vpltools.SupportedLanguages.SQL ]
        cls.ignore_files.append(cls.use_database)
        super().setUpClass()
        
        use_database_path = os.path.join(cls.THIS_DIR_NAME, cls.use_database)
        
        if not cls.use_database:
            raise ValueError(f"Cannot execute query - no database specified! Define class attribute '{cls.__name__}.use_database'")

        if cls.backend == SupportedSQLBackends.SQLite3:
            try:
                cls.db = VPLDefaultDatabase(cls.THIS_DIR_NAME)
                cls.conn = cls.db.conn
                print("Using VPL default database (vpl.db)")
            except FileNotFoundError:
                cls.db = InMemoryTestingDatabase(use_database_path)
                cls.conn = cls.db.conn
                print("Using in-memory database.")

        elif cls.backend == SupportedSQLBackends.MariaDB:
            cls.db = MariaDBPersistentDatabase(use_database_path, cls.db_user, cls.db_password, cls.db_name)
            cls.conn = cls.db.conn
            
        else:
            raise ValueError(f"RDBMS backend '{cls.backend}' is not supported. Choose between {list(SupportedSQLBackends)}.")


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if not cls.key_source_files:
            print("No pre_vpl_run.sh needed.")
            return
        
        print("Writing pre_vpl_run.sh...", end="")
        bash_file_list = " ".join([ f'"{key_file}"' for key_file in cls.key_source_files ])
        pre_run_sh_contents = (
             f'for file in {bash_file_list}\n'
            + 'do\n'
            +f'if [ -f "$file" ]; then\n'
            +f'    mv "$file" "$file{cls.mask_extension}"\n'
            # +f'    echo "$file moved."\n'
            + '    echo "Success."\n'
            + 'fi\n'
            + 'done\n')

        pre_run_sh_path = os.path.join(cls.THIS_DIR_NAME, "pre_vpl_run.sh")
        try:
            with open(pre_run_sh_path, "r") as pre_run_fo:
                old_pre_run_contents = pre_run_fo.read()
        except FileNotFoundError:
            old_pre_run_contents = None # If it doesn't exist, create it.
        
        if old_pre_run_contents != pre_run_sh_contents: # Compare to None is always False
            with open(pre_run_sh_path, "w") as pre_run_fo:
                pre_run_fo.write(pre_run_sh_contents)
        else:
            print("no changes...", end="")
        print("done.")



class TestSQLSelectQuery(TestSQLQuery):
    '''
    A TestCase class meant to test that the output of two SELECT
    queries are the same. Allows comparing records in order, or 
    out of order, and allows matching of aliased columns by ensuring 
    that all the data in each column is the same.
    '''
    permit_select_all = True
    permit_natural_join = True

    @staticmethod
    def inexplicablyNonstandardEquals(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
        '''
        pd.DataFrame.equals() did not have the behavior I expected. I expected:
        
        Returns True if df1 and df2 have identically-named columns and indexed rows 
        (raises ValueError if they do not), and identical values in each location.
        '''
        return all((df1 == df2).all())


    def testNoSelectAll(self):
        if self.permit_select_all:
            return
        
        matches = self.find_matches_in_file(r"select\s+\*")
        if matches:
            self.fail(
                msg=("\n'SELECT *' is not allowed here. Make sure that it doesn't "
                    +"appear anywhere in your submission file, even in comments. "))


    def testNoNaturalJoin(self):
        if self.permit_natural_join:
            return

        matches = self.find_matches_in_file(r"natural\s+join")
        if matches:
            self.fail(
                msg=f"\nNATURAL JOIN is not allowed here. Make sure that it doesn't " 
                    + "appear anywhere in your submission file, even in comments.")


    def find_matches_in_file(self, raw_pattern: str):
        with open(os.path.join(self.THIS_DIR_NAME, self.student_program.source_files[0]), "r") as lab_fo: # type: ignore
            lab_file_contents = lab_fo.read().lower()

        select_all_re = re.compile(raw_pattern, re.IGNORECASE)
        return select_all_re.findall(lab_file_contents)


    def compareQueries(self, key_file_name: str, lab_file_name: str, record_order_does_matter: bool = False) -> None:
        '''
        Helper function for testing the output of SELECT queries. 
        
        Raises AssertionError if the data sets returned by the queries in 
        key_file_name and lab_file_name are not identical. 
        Our notion of "identical" allows record order to differ. 
        Pass record_order_does_matter=True to change this behavior.
        The order and names of columns never matters.
        '''
        key_file_path = os.path.join(self.THIS_DIR_NAME, key_file_name)
        lab_file_path = os.path.join(self.THIS_DIR_NAME, lab_file_name)

        # Read the contents of files which contain queries.
        try:
            with open(key_file_path, 'r') as key_fo:
                key_df = self.db.run_query(key_fo.read())
        except FileNotFoundError: # File may have been masked
            with open(key_file_path+self.mask_extension, 'r') as key_fo:
                key_df = self.db.run_query(key_fo.read())

        with open(lab_file_path, 'r') as lab_fo:
            lab_df = self.db.run_query(lab_fo.read())

        # Do we have the correct shape?
        self.assertEqual(
            key_df.shape, 
            lab_df.shape, 
            msg=f"Expected {key_df.shape[0]} rows, {key_df.shape[1]} columns, "
              + f"received {lab_df.shape[0]} rows, {lab_df.shape[1]} columns.\n"
              + "Expected:\n"
              + str(key_df))

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
        

        # NOTE: The if below can't be rolled into the loop below it, because if all the 
        # columns match, then there are 0 permutations, and the loop doesn't 
        # run. So we need to check it here.
        if len(unmatched_key_columns) == 0 and len(unmatched_lab_columns) == 0:
            lab_resolution_candidate = lab_df[shared_columns]
            if not record_order_does_matter:
                lab_resolution_candidate = lab_resolution_candidate.sort_values(list(lab_resolution_candidate.columns))
                lab_resolution_candidate = lab_resolution_candidate.reset_index(drop=True)

                self.assertTrue(
                    self.inexplicablyNonstandardEquals(key_resolution_candidate, lab_resolution_candidate),
                    msg=(f"The columns were correct, but the data was not.\n"
                    +f"Expected:\n{key_df}\n\nReceived:\n{lab_df}")
                )

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

    
    def assertQueryOutputsEqual(self, key_source_file: str = ""):
        '''
        Executes the student-submitted query, and the query in the first key_source file,
        raising AssertionError if they are not identical. 
        Only the first element of self.key_source_files is used, or the specified key_source_file.
        Only one student source file is supported; if more than one is provided, there is 
        no guarantee which one will be used.
        '''
        db_err = None
        use_key_file = key_source_file if key_source_file else self.key_source_files[0]
        try:
            self.compareQueries(use_key_file, self.student_program.source_files[0])
        except pd.errors.DatabaseError as de:
            db_err = str(de)

        # Failing a test within an except complicates the traceback.
        if db_err:
            self.fail(msg=db_err)


if __name__ == "__main__":
    unittest.main()
