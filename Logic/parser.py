"""
Parser for Logic Lang
Converts tokens into an Abstract Syntax Tree (AST)
"""

from tokens import TokenType
from errors import LogicParserError


# ============================================================================
# AST Node Classes - represent different language constructs
# ============================================================================

class ASTNode:
    """Base class for all AST nodes"""

    def __repr__(self):
        fields = ', '.join(
            f"{name}={value!r}" for name, value in self.__dict__.items()
        )
        return f"{self.__class__.__name__}({fields})"


class Program(ASTNode):
    """Root node representing the entire program"""
    def __init__(self, imports, main_block):
        self.imports = imports  # List of import statements
        self.main_block = main_block  # The main block


class ImportStatement(ASTNode):
    """Represents an import statement"""
    def __init__(self, module_name):
        self.module_name = module_name


class MainBlock(ASTNode):
    """Represents the main { } block"""
    def __init__(self, statements):
        self.statements = statements  # List of statements


class PrintStatement(ASTNode):
    """Represents a print() function call"""
    def __init__(self, arguments):
        self.arguments = arguments  # List of expressions to print


class VariableDeclaration(ASTNode):
    """Represents a let variable declaration"""
    def __init__(self, name, value):
        self.name = name  # Variable name
        self.value = value  # Expression assigned to variable


class VariableAssignment(ASTNode):
    """Represents assigning a value to an existing variable"""
    def __init__(self, name, value):
        self.name = name
        self.value = value


class IfStatement(ASTNode):
    """Represents an if/else statement"""
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block  # List of statements
        self.else_block = else_block  # List of statements or None


class WhileStatement(ASTNode):
    """Represents a while loop"""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # List of statements


class ForStatement(ASTNode):
    """Represents a for loop"""
    def __init__(self, variable, start, end, body):
        self.variable = variable
        self.start = start
        self.end = end
        self.body = body  # List of statements


class FunctionDeclaration(ASTNode):
    """Represents a function definition"""
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters  # List of parameter names
        self.body = body  # List of statements


class ReturnStatement(ASTNode):
    """Represents a return statement"""
    def __init__(self, value=None):
        self.value = value  # Expression or None


class InputStatement(ASTNode):
    """Represents an input() call"""
    def __init__(self, prompt=None):
        self.prompt = prompt  # Expression or None


class BinaryOperation(ASTNode):
    """Represents binary operations like +, -, *, /, ==, etc."""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOperation(ASTNode):
    """Represents unary operations like -, not"""
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class FunctionCall(ASTNode):
    """Represents a function call"""
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments  # List of expressions


class Variable(ASTNode):
    """Represents a variable reference"""
    def __init__(self, name):
        self.name = name


class Literal(ASTNode):
    """Represents a literal value (string, number, boolean)"""
    def __init__(self, value, literal_type):
        self.value = value
        self.literal_type = literal_type  # 'string', 'number', 'boolean'


# ============================================================================
# Parser Class
# ============================================================================

class Parser:
    """Parses tokens into an Abstract Syntax Tree"""
    
    def __init__(self, tokens, filename="<unknown>"):
        """
        Initialize the parser with a list of tokens
        
        Args:
            tokens: List of Token objects from the Lexer
            filename: File name for error reporting
        """
        self.tokens = tokens
        self.position = 0
        self.filename = filename
    
    def error(self, message):
        """Raise a parser error with token information"""
        token = self.current_token()
        raise LogicParserError(
            message,
            filename=self.filename,
            line=token.line,
            column=token.column,
            token=token.value,
        )
    
    def current_token(self):
        """Get the current token without consuming it"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # Return EOF if past end
    
    def peek_token(self, offset=1):
        """Look ahead at a token"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF
    
    def advance(self):
        """Move to the next token"""
        if self.position < len(self.tokens):
            self.position += 1
    
    def skip_newlines(self):
        """Skip any newline tokens"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def expect(self, token_type):
        """
        Consume a token of the expected type or raise an error
        
        Args:
            token_type: Expected TokenType
            
        Returns:
            The matched token
        """
        if self.current_token().type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token().type.name}")
        
        token = self.current_token()
        self.advance()
        return token
    
    def match(self, *token_types):
        """Check if current token matches any of the given types"""
        return self.current_token().type in token_types
    
    def consume(self, token_type):
        """Consume a token of the given type if it matches, else return False"""
        if self.match(token_type):
            self.advance()
            return True
        return False
    
    def parse(self):
        """Parse the token stream into an AST"""
        imports = []
        
        # Parse import statements
        self.skip_newlines()
        while self.match(TokenType.IMPORT):
            imports.append(self.parse_import())
            self.skip_newlines()
        
        # Parse main block (required)
        main_block = self.parse_main_block()
        
        # Skip any trailing whitespace and expect EOF
        self.skip_newlines()
        if not self.match(TokenType.EOF):
            self.error("Expected end of file")
        
        return Program(imports, main_block)
    
    def parse_import(self):
        """Parse an import statement"""
        self.expect(TokenType.IMPORT)
        self.skip_newlines()
        
        # Accept either IDENTIFIER or MAIN keyword as import name
        if self.match(TokenType.MAIN):
            name_token = self.current_token()
            self.advance()
        elif self.match(TokenType.IDENTIFIER):
            name_token = self.current_token()
            self.advance()
        else:
            self.error("Expected module name after import")
        
        self.skip_newlines()
        
        return ImportStatement(name_token.value)
    
    def parse_main_block(self):
        """Parse the main { } block"""
        self.expect(TokenType.MAIN)
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        statements = []
        
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return MainBlock(statements)
    
    def parse_statement(self):
        """Parse a single statement"""
        self.skip_newlines()
        
        if self.match(TokenType.RBRACE, TokenType.EOF):
            return None
        
        # Print statement
        if self.match(TokenType.PRINT):
            return self.parse_print()
        
        # Variable declaration
        elif self.match(TokenType.LET):
            return self.parse_let()
        
        # If statement
        elif self.match(TokenType.IF):
            return self.parse_if()
        
        # While statement
        elif self.match(TokenType.WHILE):
            return self.parse_while()
        
        # For statement
        elif self.match(TokenType.FOR):
            return self.parse_for()
        
        # Function declaration
        elif self.match(TokenType.FUNCTION):
            return self.parse_function()
        
        # Return statement
        elif self.match(TokenType.RETURN):
            return self.parse_return()
        
        # Expression statement (assignment or function call)
        else:
            expr = self.parse_expression()
            self.skip_newlines()
            self.consume(TokenType.SEMICOLON)  # Optional semicolon
            return expr
    
    def parse_print(self):
        """Parse a print statement"""
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        
        arguments = []
        
        if not self.match(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            
            while self.consume(TokenType.COMMA):
                self.skip_newlines()
                arguments.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        self.consume(TokenType.SEMICOLON)  # Optional semicolon
        
        return PrintStatement(arguments)
    
    def parse_let(self):
        """Parse a let variable declaration"""
        self.expect(TokenType.LET)
        self.skip_newlines()
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.skip_newlines()
        self.expect(TokenType.ASSIGN)
        self.skip_newlines()
        
        value = self.parse_expression()
        
        self.skip_newlines()
        self.consume(TokenType.SEMICOLON)  # Optional semicolon
        
        return VariableDeclaration(name, value)
    
    def parse_if(self):
        """Parse an if/else statement"""
        self.expect(TokenType.IF)
        self.skip_newlines()
        self.expect(TokenType.LPAREN)
        
        condition = self.parse_expression()
        
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        then_block = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        self.skip_newlines()
        
        else_block = None
        if self.consume(TokenType.ELSE):
            self.skip_newlines()
            self.expect(TokenType.LBRACE)
            self.skip_newlines()
            
            else_block = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
                self.skip_newlines()
            
            self.expect(TokenType.RBRACE)
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while(self):
        """Parse a while loop"""
        self.expect(TokenType.WHILE)
        self.skip_newlines()
        self.expect(TokenType.LPAREN)
        
        condition = self.parse_expression()
        
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return WhileStatement(condition, body)
    
    def parse_for(self):
        """Parse a for loop"""
        self.expect(TokenType.FOR)
        self.skip_newlines()
        self.expect(TokenType.LPAREN)
        
        var_token = self.expect(TokenType.IDENTIFIER)
        variable = var_token.value
        
        self.skip_newlines()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        start = self.parse_expression()
        
        self.skip_newlines()
        self.expect(TokenType.COMMA)
        self.skip_newlines()
        
        end = self.parse_expression()
        
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return ForStatement(variable, start, end, body)
    
    def parse_function(self):
        """Parse a function declaration"""
        self.expect(TokenType.FUNCTION)
        self.skip_newlines()
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.skip_newlines()
        self.expect(TokenType.LPAREN)
        
        parameters = []
        if not self.match(TokenType.RPAREN):
            param_token = self.expect(TokenType.IDENTIFIER)
            parameters.append(param_token.value)
            
            while self.consume(TokenType.COMMA):
                self.skip_newlines()
                param_token = self.expect(TokenType.IDENTIFIER)
                parameters.append(param_token.value)
        
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return FunctionDeclaration(name, parameters, body)
    
    def parse_return(self):
        """Parse a return statement"""
        self.expect(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.RBRACE):
            value = self.parse_expression()
        
        self.skip_newlines()
        self.consume(TokenType.SEMICOLON)
        
        return ReturnStatement(value)
    
    def parse_expression(self):
        """Parse an expression"""
        return self.parse_or()
    
    def parse_or(self):
        """Parse logical OR expression"""
        left = self.parse_and()
        
        while self.match(TokenType.OR):
            op = self.current_token().value
            self.advance()
            right = self.parse_and()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_and(self):
        """Parse logical AND expression"""
        left = self.parse_not()
        
        while self.match(TokenType.AND):
            op = self.current_token().value
            self.advance()
            right = self.parse_not()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_not(self):
        """Parse logical NOT expression"""
        if self.match(TokenType.NOT):
            op = self.current_token().value
            self.advance()
            operand = self.parse_not()
            return UnaryOperation(op, operand)
        
        return self.parse_comparison()
    
    def parse_comparison(self):
        """Parse comparison expressions"""
        left = self.parse_addition()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL,
                          TokenType.LESS_THAN, TokenType.GREATER_THAN,
                          TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op = self.current_token().value
            self.advance()
            right = self.parse_addition()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_addition(self):
        """Parse addition and subtraction"""
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token().value
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_multiplication(self):
        """Parse multiplication, division, and modulo"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.current_token().value
            self.advance()
            right = self.parse_unary()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_unary(self):
        """Parse unary expressions"""
        if self.match(TokenType.MINUS, TokenType.NOT):
            op = self.current_token().value
            self.advance()
            operand = self.parse_unary()
            return UnaryOperation(op, operand)
        
        return self.parse_postfix()
    
    def parse_postfix(self):
        """Parse postfix expressions (function calls, assignment)"""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                # Function call
                self.advance()
                
                arguments = []
                if not self.match(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    
                    while self.consume(TokenType.COMMA):
                        self.skip_newlines()
                        arguments.append(self.parse_expression())
                
                self.expect(TokenType.RPAREN)
                
                if isinstance(expr, Variable):
                    expr = FunctionCall(expr.name, arguments)
                else:
                    self.error("Cannot call non-function")
            
            elif self.match(TokenType.ASSIGN):
                # Assignment
                self.advance()
                value = self.parse_expression()
                
                if isinstance(expr, Variable):
                    expr = VariableAssignment(expr.name, value)
                else:
                    self.error("Cannot assign to non-variable")
            
            else:
                break
        
        return expr
    
    def parse_primary(self):
        """Parse primary expressions (literals, variables, parenthesized expressions)"""
        
        # String literal
        if self.match(TokenType.STRING):
            value = self.current_token().value
            self.advance()
            return Literal(value, 'string')
        
        # Number literal
        elif self.match(TokenType.NUMBER):
            value = self.current_token().value
            self.advance()
            return Literal(value, 'number')
        
        # Boolean literals
        elif self.match(TokenType.TRUE):
            self.advance()
            return Literal(True, 'boolean')
        
        elif self.match(TokenType.FALSE):
            self.advance()
            return Literal(False, 'boolean')
        
        # Input function
        elif self.match(TokenType.INPUT):
            self.advance()
            self.expect(TokenType.LPAREN)
            
            prompt = None
            if not self.match(TokenType.RPAREN):
                prompt = self.parse_expression()
            
            self.expect(TokenType.RPAREN)
            return InputStatement(prompt)
        
        # Identifier (variable or function)
        elif self.match(TokenType.IDENTIFIER):
            name = self.current_token().value
            self.advance()
            return Variable(name)
        
        # Parenthesized expression
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        else:
            self.error(f"Unexpected token: {self.current_token().type.name}")
