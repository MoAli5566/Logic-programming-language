"""
Module loader for Logic Lang
Loads external .lgc modules and returns parsed module programs.
"""

import os

from lexer import Lexer
from parser import Parser
from errors import LogicRuntimeError


class Module:
    """Represents a loaded Logic Lang module."""

    def __init__(self, name, path, program):
        self.name = name
        self.path = path
        self.program = program

    def __repr__(self):
        return f"Module(name={self.name!r}, path={self.path!r})"


class ModuleLoader:
    """Loads Logic Lang modules from the file system."""

    def __init__(self, search_paths=None):
        self.search_paths = search_paths or [os.getcwd(), os.path.join(os.getcwd(), "std")]
        self.loaded_modules = {}

    def resolve_module_path(self, module_name, current_directory=None):
        candidates = []
        if current_directory:
            candidates.append(os.path.join(current_directory, f"{module_name}.lgc"))
        for base in self.search_paths:
            candidates.append(os.path.join(base, f"{module_name}.lgc"))

        for path in candidates:
            if os.path.isfile(path):
                return os.path.abspath(path)

        raise LogicRuntimeError(f"Module '{module_name}' not found", token=module_name)

    def load_module(self, module_name, current_directory=None):
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]

        module_path = self.resolve_module_path(module_name, current_directory)
        with open(module_path, "r") as source_file:
            source = source_file.read()

        lexer = Lexer(source, filename=module_path)
        tokens = lexer.tokenize()
        parser = Parser(tokens, filename=module_path)
        program = parser.parse()

        module = Module(module_name, module_path, program)
        self.loaded_modules[module_name] = module
        return module
