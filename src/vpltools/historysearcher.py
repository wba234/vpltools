import os
import unittest
import warnings
import sys

from vpltools import VPLTestCase

__unittest = True

class HistorySearcher(VPLTestCase):
    # __test__ = False
    key_source_files = []
    commands_to_find = []
    ignore_files = [
        "assignment_description.html",
        "tux.png",
        "PathsExample.drawio.svg",
        "LinuxDirectoryStructure.drawio.svg"
    ]
    command_found_emoji = {
        True    : "\N{heavy check mark}",
        False   : "\N{warning sign}"
    }

    @classmethod
    def setUpClass(cls):
        cls.set_this_dir_name()
        cls.student_program = None
        cls.files_renamed = []


    def test_each_command_in_history(self):
        student_history_files = self.find_student_files()
        if len(student_history_files) != 1:
            raise RuntimeError("Must have exactly one history file. "
                + f"Found {len(student_history_files)} files: {student_history_files}")

        self.student_history_file = student_history_files[0]
        # return
        if len(self.commands_to_find) == 0:
            self.fail(f"Empty list! Please define commands_to_find (list[str])!")
            

        max_command_len = max(len(command) for command in self.commands_to_find)
        
        # cwd = os.getcwd()
        hist_file_path = os.path.join(self.THIS_DIR_NAME, self.student_history_file)
        with open(hist_file_path, "r") as hist_fo:
            hist_file_contents = hist_fo.read()

        num_commands_found = 0
        for command in self.commands_to_find:
            command_was_found = command in hist_file_contents
            num_commands_found += 1 if command_was_found else 0
            summary_emoji = self.command_found_emoji[command_was_found]
            summary_line = f"{summary_emoji}  {command}"
            print(summary_line)

        padding = 5
        print("-" * (max_command_len + padding))
        print(f"{num_commands_found} of {len(self.commands_to_find)} commands found ({num_commands_found / len(self.commands_to_find) * 100:.0f}%)")

        if num_commands_found != len(self.commands_to_find):
            self.fail(msg=f"Expected all commands to be run, got {num_commands_found} of {len(self.commands_to_find)}")

if __name__ == "__main__":
    unittest.main()