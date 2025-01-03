import os.path
import argparse
import os

__unittest = True

class HistorySearcher:
    def __init__(self, commands_to_find):
        self.commands_to_find = commands_to_find
        self.max_command_len = max([len(command) for command in commands_to_find])

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("history_file")


    def add_command(self, command):
        self.commands_to_find.append(command)
        self.max_command_len = max(len(command), self.max_command_len)


    def get_hist_file_contents(self, history_file_name):
        cwd = os.getcwd()
        hist_file_path = os.path.join(cwd, history_file_name)
        print()
        with open(hist_file_path, "r") as hist_fo:
            hist_file_contents = hist_fo.read()

        return hist_file_contents


    def check_for_commands(self, commands, hist_file_contents):
        num_commands_found = 0
        for command in commands:
            if command in hist_file_contents:
                num_commands_found += 1
                summary_emoji = "\N{heavy check mark}"
            else:
                summary_emoji = "\N{warning sign}"

            summary_line = f"{summary_emoji}  {command}"
            print(summary_line)

        padding = 5
        print("-" * (self.max_command_len + padding))
        print(f"{num_commands_found} / {len(commands)} commands found ({num_commands_found / len(commands) * 100:.0f}%)")


    def search(self):
        args = self.parser.parse_args()
        hist_file_contents = self.get_hist_file_contents(args.history_file)
        self.check_for_commands(self.commands_to_find, hist_file_contents)

