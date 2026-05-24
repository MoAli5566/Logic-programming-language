"""
Token definitions for Logic Lang
Defines all token types used by the lexer
"""

from enum import Enum, auto

class TokenType(Enum):
    """Enumeration of all token types in Logic Lang"""
    
    # Literals
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    
    # Keywords
    IMPORT = auto()
    MAIN = auto()
    PRINT = auto()
    LET = auto()
    INPUT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()


class Token:
    """Represents a single token in the source code"""
    
    def __init__(self, token_type, value, line, column):
        """
        Initialize a token
        
        Args:
            token_type: TokenType enum value
            value: The actual value/lexeme of the token
            line: Line number in source code (1-indexed)
            column: Column number in source code (1-indexed)
        """
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        """String representation of token for debugging"""
        return f"Token({self.type.name}, {self.value!r}, {self.line}, {self.column})"
    
    def __str__(self):
        """Human-readable token representation"""
        return f"{self.type.name}: {self.value}"


# Keywords mapping - maps keyword strings to their token types
KEYWORDS = {
    'import': TokenType.IMPORT,
    'main': TokenType.MAIN,
    'print': TokenType.PRINT,
    'let': TokenType.LET,
    'input': TokenType.INPUT,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'function': TokenType.FUNCTION,
    'return': TokenType.RETURN,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
}
