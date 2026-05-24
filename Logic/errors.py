"""
Error definitions for Logic Lang
Provides structured, user-friendly error messages
"""

class LogicError(Exception):
    """Base class for Logic Lang errors."""

    def __init__(self, message, filename=None, line=None, column=None, token=None):
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        self.token = token
        super().__init__(message)

    def __str__(self):
        return self.format_error()

    def format_error(self):
        error_lines = ["Logic Error:"]
        if self.filename:
            error_lines.append(f"File: {self.filename}")
        if self.line is not None:
            location = f"Line: {self.line}"
            if self.column is not None:
                location += f", Column: {self.column}"
            error_lines.append(location)
        if self.token is not None:
            error_lines.append(f"Token: {self.token}")
        error_lines.append(f"Message: {self.message}")
        return "\n".join(error_lines)


class LogicSyntaxError(LogicError):
    """Syntax errors during lexical analysis or invalid characters."""
    pass


class LogicParserError(LogicError):
    """Parser errors when tokens do not follow grammar rules."""
    pass


class LogicRuntimeError(LogicError):
    """Runtime errors during program execution."""
    pass
