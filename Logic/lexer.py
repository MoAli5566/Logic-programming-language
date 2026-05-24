"""
Lexer for Logic Lang
Converts source code into a stream of tokens
"""

from tokens import Token, TokenType, KEYWORDS
from errors import LogicSyntaxError


class Lexer:
    """Tokenizes Logic Lang source code"""
    
    def __init__(self, source, filename="<unknown>"):
        """
        Initialize the lexer with source code
        
        Args:
            source: String containing the Logic Lang source code
            filename: File name for error reporting
        """
        self.source = source
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def error(self, message, token=None):
        """Raise a lexer error with location information"""
        raise LogicSyntaxError(
            message,
            filename=self.filename,
            line=self.line,
            column=self.column,
            token=token,
        )
    
    def peek(self, offset=0):
        """
        Look at a character without consuming it
        
        Args:
            offset: How many characters ahead to look
            
        Returns:
            Character at that position, or None if at end of file
        """
        pos = self.position + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self):
        """Move to the next character in the source"""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self):
        """Skip whitespace characters (except newlines, which may be significant)"""
        while self.peek() and self.peek() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip comments starting with // until end of line"""
        if self.peek() == '/' and self.peek(1) == '/':
            while self.peek() and self.peek() != '\n':
                self.advance()
    
    def read_string(self):
        """Read a string literal and return its value"""
        quote = self.peek()
        self.advance()  # Skip opening quote
        
        value = ''
        while self.peek() and self.peek() != quote:
            if self.peek() == '\\':
                self.advance()
                # Handle escape sequences
                next_char = self.peek()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == 'r':
                    value += '\r'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote:
                    value += quote
                else:
                    value += next_char or ''
                self.advance()
            else:
                value += self.peek()
                self.advance()
        
        if not self.peek():
            self.error("Unterminated string literal")
        
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self):
        """Read a number (integer or float) and return its value"""
        value = ''
        has_dot = False
        
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            if self.peek() == '.':
                if has_dot:
                    break  # Second dot ends the number
                has_dot = True
            value += self.peek()
            self.advance()
        
        return float(value) if has_dot else int(value)
    
    def read_identifier(self):
        """Read an identifier or keyword and return its value"""
        value = ''
        
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.peek()
            self.advance()
        
        return value
    
    def tokenize(self):
        """
        Tokenize the entire source code
        
        Returns:
            List of Token objects
        """
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if self.position >= len(self.source):
                break
            
            # Store token position
            token_line = self.line
            token_column = self.column
            
            current = self.peek()
            
            # Skip comments
            if current == '/' and self.peek(1) == '/':
                self.skip_comment()
                continue
            
            # Newlines
            if current == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', token_line, token_column))
                self.advance()
            
            # Strings
            elif current in ('"', "'"):
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, token_line, token_column))
            
            # Numbers
            elif current.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, token_line, token_column))
            
            # Identifiers and keywords
            elif current.isalpha() or current == '_':
                value = self.read_identifier()
                
                # Check if it's a keyword
                if value in KEYWORDS:
                    token_type = KEYWORDS[value]
                    self.tokens.append(Token(token_type, value, token_line, token_column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, value, token_line, token_column))
            
            # Operators and delimiters
            elif current == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', token_line, token_column))
                self.advance()
            
            elif current == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', token_line, token_column))
                self.advance()
            
            elif current == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', token_line, token_column))
                self.advance()
            
            elif current == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', token_line, token_column))
                self.advance()
            
            elif current == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', token_line, token_column))
                self.advance()
            
            elif current == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', token_line, token_column))
                self.advance()
            
            elif current == '.':
                self.tokens.append(Token(TokenType.DOT, '.', token_line, token_column))
                self.advance()
            
            elif current == ':':
                self.tokens.append(Token(TokenType.COLON, ':', token_line, token_column))
                self.advance()
            
            elif current == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', token_line, token_column))
                self.advance()
            
            elif current == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', token_line, token_column))
                self.advance()
            
            elif current == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', token_line, token_column))
                self.advance()
            
            elif current == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', token_line, token_column))
                self.advance()
            
            elif current == '%':
                self.tokens.append(Token(TokenType.MODULO, '%', token_line, token_column))
                self.advance()
            
            elif current == '=':
                if self.peek(1) == '=':
                    self.tokens.append(Token(TokenType.EQUAL, '==', token_line, token_column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', token_line, token_column))
                    self.advance()
            
            elif current == '!':
                if self.peek(1) == '=':
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', token_line, token_column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', token_line, token_column))
                    self.advance()
            
            elif current == '<':
                if self.peek(1) == '=':
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', token_line, token_column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.LESS_THAN, '<', token_line, token_column))
                    self.advance()
            
            elif current == '>':
                if self.peek(1) == '=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', token_line, token_column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.GREATER_THAN, '>', token_line, token_column))
                    self.advance()
            
            else:
                self.error(f"Unexpected character: {current!r}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        
        return self.tokens
