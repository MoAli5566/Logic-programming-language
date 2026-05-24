"""
Builtins compatibility module for Logic Lang.

This wrapper exists so the project can include a `builtins.py` file
while avoiding conflict with Python's own builtins module.
"""

from logic_builtins import BuiltinFunction, BuiltinRegistry

__all__ = ["BuiltinFunction", "BuiltinRegistry"]
