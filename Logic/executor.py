"""
Executor for Logic Lang
Interprets the Abstract Syntax Tree
"""

import os
import sys
from logic_builtins import BuiltinRegistry
from errors import LogicRuntimeError
from module_loader import ModuleLoader
from parser import (
    ImportStatement, MainBlock, PrintStatement,
    VariableDeclaration, VariableAssignment, IfStatement,
    WhileStatement, ForStatement, FunctionDeclaration,
    ReturnStatement, InputStatement, BinaryOperation,
    UnaryOperation, FunctionCall, Variable, Literal
)


class ReturnValue(Exception):
    """Exception used to implement return statements"""
    def __init__(self, value):
        self.value = value


class ExecutionContext:
    """Represents the execution context (variables, functions, modules, and built-ins)"""
    
    def __init__(self, parent=None, builtins=None):
        """
        Initialize an execution context
        
        Args:
            parent: Parent context for nested scopes
            builtins: Built-in function registry shared across contexts
        """
        self.parent = parent
        self.variables = {}
        self.functions = {}
        self.modules = {}
        self.builtins = builtins if builtins is not None else getattr(parent, 'builtins', None)
    
    def define_variable(self, name, value):
        """Define a variable in this scope"""
        self.variables[name] = value
    
    def get_variable(self, name):
        """Get a variable value, checking parent scopes"""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise LogicRuntimeError(f"Undefined variable: {name}", token=name)
    
    def set_variable(self, name, value):
        """Set a variable value, checking parent scopes"""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set_variable(name, value)
        else:
            self.variables[name] = value
    
    def define_function(self, name, function):
        """Define a function in this scope"""
        self.functions[name] = function
    
    def get_function(self, name):
        """Get a function, checking parent scopes"""
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise LogicRuntimeError(f"Undefined function: {name}", token=name)
    
    def define_module(self, name, module):
        """Define a loaded module in this scope"""
        self.modules[name] = module
    
    def get_module(self, name):
        """Get a module from this scope"""
        if name in self.modules:
            return self.modules[name]
        elif self.parent:
            return self.parent.get_module(name)
        else:
            raise LogicRuntimeError(f"Undefined module: {name}", token=name)
    
    def get_builtin(self, name):
        """Get a built-in function from the current or parent scopes"""
        if self.builtins and self.builtins.has(name):
            return self.builtins.get(name)
        elif self.parent:
            return self.parent.get_builtin(name)
        return None


class Executor:
    """Executes Logic Lang AST"""
    
    def __init__(self, debug=False):
        """Initialize the executor with a global context"""
        self.debug = debug
        self.indent_level = 0
        self.builtins = BuiltinRegistry()
        self.module_loader = ModuleLoader()
        self.global_context = ExecutionContext(parent=None, builtins=self.builtins)
    
    def _debug(self, message):
        if self.debug:
            prefix = "  " * self.indent_level
            print(f"[DEBUG] {prefix}{message}")
    
    def execute(self, program, filename="<unknown>"):
        """
        Execute a program
        
        Args:
            program: Program AST node
            filename: Source file name for error reporting
        """
        self.filename = filename
        for import_stmt in program.imports:
            self.execute_import(import_stmt)
        
        if program.main_block:
            self.execute_main_block(program.main_block)
    
    def execute_import(self, import_stmt):
        """Execute an import statement by loading an external module"""
        self._debug(f"Importing module: {import_stmt.module_name}")
        module = self.module_loader.load_module(
            import_stmt.module_name,
            current_directory=os.path.dirname(self.filename) if self.filename else None,
        )

        module_context = ExecutionContext(parent=self.global_context, builtins=self.builtins)
        self._debug(f"Executing module: {module.name} from {module.path}")
        self.indent_level += 1
        self.execute_block(module.program.main_block.statements, module_context)
        self.indent_level -= 1

        self.global_context.define_module(import_stmt.module_name, module)
        module.context = module_context
        self._merge_module_scope(module_context)
    
    def execute_main_block(self, main_block):
        """Execute the main block"""
        self.execute_block(main_block.statements, self.global_context)
    
    def execute_block(self, statements, context):
        """Execute a block of statements"""
        for statement in statements:
            self.execute_statement(statement, context)

    def _merge_module_scope(self, module_context):
        """Make module definitions available to the global context."""
        for name, value in module_context.variables.items():
            if name not in self.global_context.variables:
                self.global_context.define_variable(name, value)
        for name, function in module_context.functions.items():
            if name not in self.global_context.functions:
                self.global_context.define_function(name, function)
    
    def execute_statement(self, statement, context):
        """Execute a single statement"""
        self._debug(f"Statement: {statement}")
        
        if isinstance(statement, PrintStatement):
            self.execute_print(statement, context)
        
        elif isinstance(statement, VariableDeclaration):
            self.execute_variable_declaration(statement, context)
        
        elif isinstance(statement, VariableAssignment):
            self.execute_variable_assignment(statement, context)
        
        elif isinstance(statement, IfStatement):
            self.execute_if(statement, context)
        
        elif isinstance(statement, WhileStatement):
            self.execute_while(statement, context)
        
        elif isinstance(statement, ForStatement):
            self.execute_for(statement, context)
        
        elif isinstance(statement, FunctionDeclaration):
            self.execute_function_declaration(statement, context)
        
        elif isinstance(statement, ReturnStatement):
            self.execute_return(statement, context)
        
        elif isinstance(statement, FunctionCall):
            self.evaluate_function_call(statement, context)
    
    def execute_print(self, statement, context):
        """Execute a print statement"""
        values = [self.evaluate_expression(arg, context) for arg in statement.arguments]
        builtin_print = context.get_builtin("print")
        if builtin_print:
            builtin_print.call(values, context)
        else:
            print(' '.join(self.value_to_string(value) for value in values))
    
    def execute_variable_declaration(self, statement, context):
        """Execute a variable declaration (let x = value)"""
        value = self.evaluate_expression(statement.value, context)
        context.define_variable(statement.name, value)
    
    def execute_variable_assignment(self, statement, context):
        """Execute a variable assignment (x = value)"""
        value = self.evaluate_expression(statement.value, context)
        context.set_variable(statement.name, value)
    
    def execute_if(self, statement, context):
        """Execute an if/else statement"""
        condition = self.evaluate_expression(statement.condition, context)
        
        if self.is_truthy(condition):
            self.execute_block(statement.then_block, context)
        elif statement.else_block:
            self.execute_block(statement.else_block, context)
    
    def execute_while(self, statement, context):
        """Execute a while loop"""
        while self.is_truthy(self.evaluate_expression(statement.condition, context)):
            try:
                self.execute_block(statement.body, context)
            except ReturnValue:
                raise
    
    def execute_for(self, statement, context):
        """Execute a for loop"""
        # Create a new context for the loop variable
        loop_context = ExecutionContext(context)
        
        start = self.evaluate_expression(statement.start, context)
        end = self.evaluate_expression(statement.end, context)
        
        # Convert to integers
        try:
            start = int(start)
            end = int(end)
        except (ValueError, TypeError):
            raise LogicRuntimeError(f"For loop bounds must be numbers", token=statement.variable)
        
        # Loop through range
        for i in range(start, end):
            loop_context.define_variable(statement.variable, i)
            try:
                self.execute_block(statement.body, loop_context)
            except ReturnValue:
                raise
    
    def execute_function_declaration(self, statement, context):
        """Execute a function declaration"""
        # Store the function definition
        context.define_function(statement.name, statement)
    
    def execute_return(self, statement, context):
        """Execute a return statement"""
        value = None
        if statement.value:
            value = self.evaluate_expression(statement.value, context)
        raise ReturnValue(value)
    
    def evaluate_expression(self, expression, context):
        """Evaluate an expression and return its value"""
        self._debug(f"Evaluate: {expression}")
        
        if isinstance(expression, Literal):
            return expression.value
        
        elif isinstance(expression, Variable):
            return context.get_variable(expression.name)
        
        elif isinstance(expression, BinaryOperation):
            return self.evaluate_binary_operation(expression, context)
        
        elif isinstance(expression, UnaryOperation):
            return self.evaluate_unary_operation(expression, context)
        
        elif isinstance(expression, FunctionCall):
            return self.evaluate_function_call(expression, context)
        
        elif isinstance(expression, InputStatement):
            return self.evaluate_input(expression, context)
        
        else:
            raise LogicRuntimeError(f"Unknown expression type: {type(expression)}")
    
    def evaluate_binary_operation(self, expr, context):
        """Evaluate a binary operation"""
        left = self.evaluate_expression(expr.left, context)
        right = self.evaluate_expression(expr.right, context)
        op = expr.operator
        
        # Arithmetic operations
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif op == '%':
            return left % right
        
        # Comparison operations
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        
        # Logical operations
        elif op == 'and':
            return self.is_truthy(left) and self.is_truthy(right)
        elif op == 'or':
            return self.is_truthy(left) or self.is_truthy(right)
        
        else:
            raise LogicRuntimeError(f"Unknown binary operator: {op}", token=op)
    
    def evaluate_unary_operation(self, expr, context):
        """Evaluate a unary operation"""
        operand = self.evaluate_expression(expr.operand, context)
        op = expr.operator
        
        if op == '-':
            return -operand
        elif op == '!' or op == 'not':
            return not self.is_truthy(operand)
        else:
            raise LogicRuntimeError(f"Unknown unary operator: {op}", token=op)
    
    def evaluate_function_call(self, expr, context):
        """Evaluate a function call"""
        self._debug(f"FunctionCall: {expr.name}({', '.join(str(arg) for arg in expr.arguments)})")
        builtin = context.get_builtin(expr.name)
        if builtin:
            arguments = [self.evaluate_expression(arg, context) for arg in expr.arguments]
            return builtin.call(arguments, context)

        try:
            func_def = context.get_function(expr.name)
        except LogicRuntimeError:
            raise LogicRuntimeError(f"Undefined function: {expr.name}", token=expr.name)

        if len(expr.arguments) != len(func_def.parameters):
            raise LogicRuntimeError(
                f"Function {expr.name}() takes {len(func_def.parameters)} arguments, got {len(expr.arguments)}",
                token=expr.name,
            )

        func_context = ExecutionContext(context, builtins=self.builtins)
        for param, arg in zip(func_def.parameters, expr.arguments):
            arg_value = self.evaluate_expression(arg, context)
            func_context.define_variable(param, arg_value)

        self.indent_level += 1
        try:
            self.execute_block(func_def.body, func_context)
            return None
        except ReturnValue as ret:
            return ret.value
        finally:
            self.indent_level -= 1
    
    def evaluate_input(self, expr, context):
        """Evaluate an input() call"""
        prompt = ""
        if expr.prompt:
            prompt = self.value_to_string(self.evaluate_expression(expr.prompt, context))
        
        return input(prompt)
    
    def is_truthy(self, value):
        """Determine if a value is truthy in Logic Lang"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return len(value) > 0
        elif value is None:
            return False
        else:
            return True
    
    def value_to_string(self, value):
        """Convert a value to its string representation"""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return ""
        else:
            return str(value)
