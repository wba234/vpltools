import os
import re
import abc
import enum
import subprocess

from typing import Type

class NoProgramError(RuntimeError):
    pass

class UnsupportedFeatureError(RuntimeError):
    pass


class SupportedLanguage(abc.ABC):
    def __init__(self, name: str, extension: str):
        self.name = name
        self.extension = extension

    def __hash__(self):
        '''
        Provided to that this can be used as the key in a dictionary.
        '''
        return hash(self.name)


class SupportedLanguageProgram(abc.ABC):
    '''
    Represents a program written in one of the languages supported by this package.
    This is an abstract base class, which is not instantiated directly. It is intended
    to be extended into another class for each supported language.
    '''
    def __init__(self, 
                 language: SupportedLanguage, 
                 compilation_commands: list[str], 
                 main_file_base_name: str, 
                 executable_dir: str,
                 executable_name: str,
                 source_files: list[str],
                 output_file_name: str) -> None:
        self.language = language
        self.compilation_commands = compilation_commands
        self.main_file_base_name = main_file_base_name
        self.executable_dir = executable_dir
        self.executable_name = executable_name
        self.source_files = source_files
        self.output_file_name = output_file_name


    @abc.abstractmethod
    def compilationCommand(self):
        '''
        Abstract method to ensure individual languages implement their respective 
        compilation commands. These should raise RunTimeError if compilation fails.
        '''
        raise NotImplementedError


    def compile(self, use_dir, recompile=False):
        '''
        Compile the program represented by the calling object. If the target program
        already exists, compilation is skipped, unless the recompile flag is set.
        '''
        if os.path.exists(os.path.join(self.executable_dir, self.executable_name)) and not recompile:
            return
        
        command = self.compilationCommand()

        # Interpreted languages don't need compilation
        if command is None:
            return
        
        # Try the supplied compilation command
        compilation_process = subprocess.run(
            command,
            cwd=use_dir
        )
        # If that fails, try make
        if compilation_process.returncode:
            compilation_process = subprocess.run(
                ["make"],
                cwd=use_dir
            )
        # If that fails, give up.
        if compilation_process.returncode:
            raise RuntimeError(
                f"Compilation failed!\n"
                + f"command={command}\n"
                + f"stdout={compilation_process.stdout}\n"
                + f"stderr={compilation_process.stderr}\n"
            )


    @abc.abstractmethod
    def run(self, cli_args: list[str], input="", **kwargs) -> subprocess.CompletedProcess:
        '''
        Executes the program represented by the calling object in a subprocess.
        '''
        raise NotImplementedError
        


class CProgram(SupportedLanguageProgram):
    '''
    Represents a program written in C, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        return super().__init__(
            SupportedLanguages.C, # type: ignore
            [ "gcc", "-o", executable_name ] + source_files + ["-lm"], 
            "main", 
            executable_dir,
            executable_name,
            source_files, 
            output_file_name)


    def compilationCommand(self):
        return self.compilation_commands
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.executable_name, *cli_args], input=input, **kwargs)

    

class CPPProgram(SupportedLanguageProgram):
    '''
    Represents a program written in C++, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        return super().__init__(
            SupportedLanguages.CPP, # type: ignore
            [ "g++", "-o", executable_name] + source_files + ["-lm"], 
            "main", 
            executable_dir,
            executable_name,
            source_files, 
            output_file_name)


    def compilationCommand(self):
        return self.compilation_commands
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.executable_name, *cli_args], input=input, **kwargs)
    


class JavaProgram(SupportedLanguageProgram):
    '''
    Represents a program written in Java, 
    e.g., a student's submission, or an instructor's key program.
    '''
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        '''
        Note that executable_name
        '''
        super().__init__(SupportedLanguages.Java, ["javac"], "main", executable_dir, executable_name, source_files, output_file_name) # type: ignore
        self.find_main_and_set_exec_name()
    

    def compilationCommand(self):
        for source_file in self.source_files:
            with open(os.path.join(self.executable_dir, source_file), "r") as fp:
                file_contents = fp.read()
                if re.search("^\\s*package\\s*.*;", file_contents, flags=re.MULTILINE) is not None:
                    raise UnsupportedFeatureError("Running Java packages is not supported by vpltools. Please remove the package statements.")

        return self.compilation_commands + self.source_files


    def run(self, cli_args, input="", **kwargs):
        return subprocess.run(["java", self.executable_name, *cli_args], input=input, **kwargs)
    

    def find_main_and_set_exec_name(self) -> str:
        for file in self.source_files:
            with open(os.path.join(self.executable_dir, file), "r") as fo:
                main_matches = re.findall(r"public\s+static\s+void\s+main", fo.read())
                if main_matches:
                    self.executable_name = file.split(".")[0]
                    return self.executable_name
        raise NoProgramError("Java program has no (public static void) main function!")



class PythonProgram(SupportedLanguageProgram):
    '''
    Represents a program written in Python,
    e.g., a student's submission, or an instructor's key program.
    '''
    PYTHON_COMMAND = "python3"
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
        exec_name = ""
        if len(source_files) == 0:
            raise ValueError("No input files found!")
        elif len(source_files) == 1:
            exec_name = source_files[0]
        elif len(source_files) > 1:
            if "main" in source_files:
                exec_name = source_files[source_files.index("main")]
            else:
                raise ValueError(f"If you have more than 1 file, you must name one of them main.py! Found {source_files}")

        return super().__init__(
            SupportedLanguages.Python, # type: ignore
            [],
            executable_dir,
            exec_name,
            source_files[0], 
            source_files, 
            output_file_name=None) # type: ignore


    def compilationCommand(self):
        return None
    

    def run(self, cli_args, input="", **kwargs):
        return subprocess.run([self.PYTHON_COMMAND, self.executable_name, *cli_args], input=input, **kwargs)



class SQLQuery(SupportedLanguageProgram):
    '''
    Represents a SELECT query, written in SQL. Could be some other
    statement which produces a result set.
    '''
    def __init__(self, executable_dir: str, executable_name: str, source_files: list[str], output_file_name: str):
            if len(source_files) != 1:
                raise ValueError(f"Too many SQL files! Only one SQL file is supported. Found:\n {source_files}")
            super().__init__(
                SupportedLanguages.SQL, # type: ignore
                [],
                "",
                executable_dir,
                executable_name,
                source_files,
                output_file_name
            )


    def compilationCommand(self):
        return None
    
    
    def run(self, cli_args, input="", **kwargs): # type: ignore
        return None
    
    

class SupportedLanguages(enum.Enum):
    C = SupportedLanguage("C", ".c")
    CPP = SupportedLanguage("C++", ".cpp")
    SQL = SupportedLanguage("SQL", ".sql")
    Java = SupportedLanguage("Java", ".java")
    Python = SupportedLanguage("Python", ".py")


OBJECT_REPRESENTING_PROGRAM_IN_LANGUAGE: dict[SupportedLanguages, Type[SupportedLanguageProgram]] = {
    SupportedLanguages.C        :   CProgram,
    SupportedLanguages.CPP      :   CPPProgram,
    SupportedLanguages.Java     :   JavaProgram,
    SupportedLanguages.Python   :   PythonProgram,
    SupportedLanguages.SQL      :   SQLQuery
}
