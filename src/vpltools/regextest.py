
import re
from vpltools import VPLTestCase

__unittest = True # Keep, to silence tracebacks.

# TODO: These should both use match, or fullmatch, or provide a flag.
# class RegexTestCase(unittest.TestCase):
class RegexTestCase(VPLTestCase):
    TEXT = "text"
    FIND = "find"
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


    def match_and_capture_text(self, pattern: str, text_to_match_and_capture: dict[str, str], force_no_match=False):
        '''
        pattern should be returned by exerciseN(), ...
        '''
        test_pattern = re.compile(pattern)
        match = test_pattern.match(text_to_match_and_capture[self.TEXT])
        # match = test_pattern.findall(text_to_match_and_capture[self.TEXT])

        if text_to_match_and_capture[self.FIND] is not None:
            self.assertIsNotNone(
                match, 
                msg=f"The pattern {pattern} didn't match '{text_to_match_and_capture[self.FIND]}', but should have.")
        elif text_to_match_and_capture[self.FIND] is None and force_no_match:
            self.assertIsNone(
                match,
                msg=f"The pattern {pattern} matched '{match}' in {text_to_match_and_capture[self.TEXT]}, but shouldn't have."
            )
    
        if text_to_match_and_capture[self.CAPT] is not None:
            captured = None
            if match is not None:
                captured = match.group(1)

            self.assertEqual(
                captured, 
                text_to_match_and_capture[self.CAPT], 
                msg=f"The captured '{captured}' didn't match the expected text '{text_to_match_and_capture[self.CAPT]}'")
        else:
            captured = None
            if match is not None:
                captured = match.group(1)

            self.assertIsNone(
                match,
                msg=f"'{captured}' was captured, but shouldn't have been."
            )
