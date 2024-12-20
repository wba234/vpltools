'''
Currently abandoned.

I don't know of a good way to make the unittests use a 
shared subclass. The idea was to make a base class that would
do nothing but call tearDownClass. But this method needs to know the 
name of the class, and the file in which it is located.

The base class need the globals(), and __file__ information from the
derived class.

If a base class can make sure that a derived class knows it's own name, 
and __file__ value, then this will work. Getting the former from globals() 
was always a hack.

'''

import unittest
import abc

import findmodules
import make_vpl_evaluate_cases

class VPLunittest(unittest.TestCase, abc.ABC):

    # @abc.abstractmethod
    # def storeGlobals(cls) -> None:
    #     raise NotImplementedError
    

    # @abc.abstractmethod
    # def getGlobals(cls) -> dict[str, any]:
    #     raise NotImplementedError
    

    # @abc.abstractmethod
    # def getFileModule(cls) -> str:
    #     raise NotImplementedError
    
    @classmethod
    def getFileModule(self) -> str:
        print("Hi.")
        return __file__

    @classmethod
    def getTestNames(cls) -> str:
        return cls.__dict__
    
    @classmethod
    def tearDownClass(cls) -> None:
        # findmodules.make_vpl_evaluate_cases(__file__, cls.getGlobals(), include_pylint=False)
        # findmodules.make_vpl_evaluate_cases(__file__, globals(), include_pylint=False)
        make_vpl_evaluate_cases.make_vpl_evaluate_cases(cls.getFileModule(), globals(), include_pylint=False)
        return super().tearDownClass()
