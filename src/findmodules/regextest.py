import unittest
import re

__unittest = True # Keep, to silence tracebacks.

class RegexTestCase(unittest.TestCase):
    TEXT = "text"
    CAPT = "capture"
    def match_text(self, pattern: str, text_to_match: str, negate_match=False):
        '''
        pattern should be returned by exerciseN(), where N is one of the assigned exercise numbers.
        '''
        test_pattern = re.compile(pattern)
        match = test_pattern.fullmatch(text_to_match)
        if negate_match:
            match = True if match is None else None
        self.assertIsNotNone(
            match, 
            msg=f"The pattern didn't match '{text_to_match}', but should have.")


    def match_and_capture_text(self, pattern: str, text_to_match_and_capture: dict[str, str]):
        '''
        pattern should be returned by exerciseN(), ...
        '''
        test_pattern = re.compile(pattern)
        match = test_pattern.fullmatch(text_to_match_and_capture[self.TEXT])
        self.assertIsNotNone(
            match, 
            msg=f"The pattern didn't match '{text_to_match_and_capture}', but should have.")
        
        captured = match.group(1)
        self.assertEqual(
            captured, 
            text_to_match_and_capture[self.CAPT], 
            msg=f"The captured text '{captured}' didn't match the expected text '{text_to_match_and_capture[self.CAPT]}'")