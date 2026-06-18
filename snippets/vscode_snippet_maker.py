'''
Turns example code files into a VSCode snippets file. This should be run to 
generate a new snippets file if new test types (subclasses of VPLTestCase)
are added to vpltools.
'''
import os.path
from dataclasses import dataclass

snippet_file_preamble = (
'''
	// Place your vpltools workspace snippets here. Each snippet is defined under a snippet name and has a scope, prefix, body and 
	// description. Add comma separated ids of the languages where the snippet is applicable in the scope field. If scope 
	// is left empty or omitted, the snippet gets applied to all languages. The prefix is what is 
	// used to trigger the snippet and the body will be expanded and inserted. Possible variables are: 
	// $1, $2 for tab stops, $0 for the final cursor position, and ${1:label}, ${2:another} for placeholders. 
	// Placeholders with the same ids are connected.
	// Example:
	// "Print to console": {
	// 	"scope": "javascript,typescript",
	// 	"prefix": "log",
	// 	"body": [
	// 		"console.log('$1');",
	// 		"$2"
	// 	],
	// 	"description": "Log output to console"
	// }
'''
)
snippets_file_json_framework = (
'''
\t"{}_test_case":{{
\t\t"scope": "python",
\t\t"prefix": "test_{}",
\t\t"isFileTemplate": true,
\t\t"body": [
{}        ]
    }},
'''
)

@dataclass
class Snippet:
    file_name: str
    content_replacements: list[str]
    metadata_replacements: list[str]
    file_contents: str = "" # Modified in place as execution proceeds.

    # def get_file_contents(self):
    #     with open(os.path.join(os.path.dirname(__file__)), self.file_name) as fo:
    #         return fo.read()


    def format_variables(self):
        for i, var_name in enumerate(self.content_replacements):
            if var_name is None:
                continue

            self.file_contents = self.file_contents.replace(var_name, f"${{{i}:{var_name}}}")


    @staticmethod
    def format_body(fo) -> str:
        body = ""
        for line in fo:
            line = line.replace('"', '\\"')
            line = line.replace('\n', '",\n',)
            body += 3 * "\t" + "\"" + line

        body += 3 * "\t" + "\"\",\n"
        return body
    
    def create_vscode_snippet_entry(self) -> str:
        fo = open(os.path.join(os.path.dirname(__file__), self.file_name), "r")
        self.file_contents = self.format_body(fo)
        self.format_variables()
        self.file_contents = snippets_file_json_framework.format(*self.metadata_replacements, self.file_contents)

        return self.file_contents

# Order of snippet variables given by index, 
# 0 is the last position, so ignore with None.
py_replacements = [
    None,
    "test_class_name",
    "key_program_source.ext",
    "test_function_name",
]
py_metadata_replacements = [
    "vpl",
    "python",
]
python_snippet = Snippet("python_test_snippet.py", py_replacements, py_metadata_replacements)


sql_replacements = [
    None,
    "test_class_name",
    "correct_query.sql",
    "db_init_file.sql",
    "test_method_name"
]
sql_metadata_replacements = [
    "sql_select",
    "sql_select",
]
sql_select_snippet = Snippet("sql_select_test_snippet.py", sql_replacements, sql_metadata_replacements)

regex_replacements = [
    None,
    "test_class_name",
    "test_match_method_name",
    "3.14159",
    "exerciseN",
    "test_capture_method_name",
    "file://localhost:4040/zip_file",
    "None",
    "localhost",
    "exerciseN"
]
regex_metadata_replacements = [
    "regex",
    "regex",
]
regex_snippet = Snippet("regex_test_snippet.py", regex_replacements, regex_metadata_replacements)

e2e_replacements = [
    None,
    "test_class_name",
    "test_method_name",
    "Hello World!"
]
e2e_metadata_replacements = [
    "end_to_end",
    "end_to_end",
]
e2e_snippet = Snippet("end_to_end_test_snippet.py", e2e_replacements, e2e_metadata_replacements)

instructions = (
'''
REMEMBER:
- Test files should start with "test".
- Test methods should also start with "test".

To run tests, you can use the command
$ python3 -m unittest
'''
)


def main():
    vscode_snippets_file_name = "vpltools.code-snippets"
    snippets_file = open(
        os.path.join(os.path.dirname(__file__), vscode_snippets_file_name), "w"
    )
    snippets_file.write("{")
    snippets_file.write(snippet_file_preamble)

    snippets = [
        python_snippet,
        sql_select_snippet,
        regex_snippet,
        e2e_snippet,
    ]
    for snippet in snippets:
        snippets_file.write(snippet.create_vscode_snippet_entry())

    snippets_file.write("}")
    snippets_file.close()


if __name__ == "__main__":
    main()
