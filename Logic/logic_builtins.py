"""
Built-in functions for Logic Lang
Defines shared built-in functionality in a centralized registry.
"""

import os
import random
import time

from errors import LogicRuntimeError


class BuiltinFunction:
    """Represents a built-in function exposed to Logic Lang."""

    def __init__(self, name, handler, min_args=0, max_args=None, description=""):
        self.name = name
        self.handler = handler
        self.min_args = min_args
        self.max_args = max_args
        self.description = description

    def call(self, arguments, context):
        if len(arguments) < self.min_args:
            raise LogicRuntimeError(
                f"{self.name}() requires at least {self.min_args} arguments",
                token=self.name
            )
        if self.max_args is not None and len(arguments) > self.max_args:
            raise LogicRuntimeError(
                f"{self.name}() accepts at most {self.max_args} arguments",
                token=self.name
            )
        return self.handler(arguments, context)


class BuiltinRegistry:
    """Registry for Logic Lang built-in functions."""

    def __init__(self):
        self._builtins = {}
        self.register_defaults()

    def register(self, builtin_function):
        self._builtins[builtin_function.name] = builtin_function

    def get(self, name):
        return self._builtins.get(name)

    def has(self, name):
        return name in self._builtins

    def register_defaults(self):
        self.register(BuiltinFunction("print", self._print, min_args=0, max_args=None,
                                      description="Print values to the console."))
        self.register(BuiltinFunction("input", self._input, min_args=0, max_args=1,
                                      description="Read a line of text from the user."))
        self.register(BuiltinFunction("len", self._len, min_args=1, max_args=1,
                                      description="Return the length of a value."))
        self.register(BuiltinFunction("type", self._type, min_args=1, max_args=1,
                                      description="Return the type of a value."))
        self.register(BuiltinFunction("time", self._time, min_args=0, max_args=0,
                                      description="Return the current Unix timestamp."))
        self.register(BuiltinFunction("random", self._random, min_args=0, max_args=0,
                                      description="Return a random number between 0 and 1."))
        self.register(BuiltinFunction("clear", self._clear, min_args=0, max_args=0,
                                      description="Clear the console output."))
        self.register(BuiltinFunction("str", self._str, min_args=1, max_args=1,
                                      description="Convert a value to a string."))
        self.register(BuiltinFunction("int", self._int, min_args=1, max_args=1,
                                      description="Convert a value to an integer."))
        self.register(BuiltinFunction("float", self._float, min_args=1, max_args=1,
                                      description="Convert a value to a float."))

    def _print(self, arguments, context):
        converted = [self._stringify_value(value) for value in arguments]
        print(" ".join(converted))
        return None

    def _input(self, arguments, context):
        prompt = self._stringify_value(arguments[0]) if arguments else ""
        return input(prompt)

    def _len(self, arguments, context):
        value = arguments[0]
        try:
            return len(value)
        except TypeError:
            raise LogicRuntimeError(f"len() argument must be a value with length", token="len")

    def _type(self, arguments, context):
        value = arguments[0]
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, str):
            return "string"
        if isinstance(value, (int, float)):
            return "number"
        if value is None:
            return "null"
        return type(value).__name__

    def _time(self, arguments, context):
        return time.time()

    def _random(self, arguments, context):
        return random.random()

    def _clear(self, arguments, context):
        command = "cls" if os.name == "nt" else "clear"
        os.system(command)
        return None

    def _str(self, arguments, context):
        return self._stringify_value(arguments[0])

    def _int(self, arguments, context):
        try:
            return int(arguments[0])
        except (ValueError, TypeError):
            raise LogicRuntimeError("int() argument must be a number or numeric string", token="int")

    def _float(self, arguments, context):
        try:
            return float(arguments[0])
        except (ValueError, TypeError):
            raise LogicRuntimeError("float() argument must be a number or numeric string", token="float")

    def _stringify_value(self, value):
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return ""
        return str(value)
