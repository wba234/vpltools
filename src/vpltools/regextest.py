
import re
import vpltools
from dataclasses import dataclass

__unittest = True # Keep, to silence tracebacks.


@dataclass
class MatchTarget:
    text_to_search: str = ""
    text_to_find: str | None = ""
    text_to_capture: str | None = ""


class RegexTestCase(vpltools.VPLTestCase):
    TEXT = "text"
    FIND = "find"
    CAPT = "capture"

    # def match_text(self, pattern: str, text_to_match: str, negate_match=False):
    def match_text(self, pattern: str, match_target: MatchTarget, negate_match=False):
        '''
        Asserts that pattern matches the entirety of match_target.text_to_find. 
        Uses re.fullmatch. This method ignores match_target's text_to_find, and
        text_to_capture attributes
        '''
        test_pattern = re.compile(pattern)
        match = test_pattern.fullmatch(match_target.text_to_search)
        if negate_match:
            match = True if match is None else None
        self.assertIsNotNone(
            match, 
            msg=f"The pattern didn't match '{match_target.text_to_search}', but should have.")


    def match_and_capture_text(self, pattern: str, match_target: MatchTarget, force_no_match=False):
        '''
        Asserts that pattern matches match_target.text_to_find, and, that 
        match_target.text_to_capture was captured. match_target.text_to_find and 
        match_target.text_to_capture may both be None.
        '''
        test_pattern = re.compile(pattern)
        match = test_pattern.match(match_target.text_to_search)
        # match = test_pattern.findall(text_to_match_and_capture[self.TEXT])

        if match_target.text_to_find is not None:
            self.assertIsNotNone(
                match, 
                msg=f"The pattern {pattern} didn't match '{match_target.text_to_find}', but should have.")
        elif match_target.text_to_find is None and force_no_match:
            self.assertIsNone(
                match,
                msg=f"The pattern {pattern} matched '{match}' in {match_target.text_to_search}, but shouldn't have."
            )
    
        if match_target.text_to_capture is not None:
            captured = None
            if match is not None:
                captured = match.group(1)

            self.assertEqual(
                captured, 
                match_target.text_to_capture,
                msg=f"The captured '{captured}' didn't match the expected text '{match_target.text_to_capture}'")
        else:
            captured = None
            if match is not None:
                captured = match.group(1)

            self.assertIsNone(
                match,
                msg=f"'{captured}' was captured, but shouldn't have been."
            )
