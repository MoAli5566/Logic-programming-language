"""
Logic Lang Interpreter
Main entry point for running Logic Lang programs
"""

import argparse
import sys
from dataclasses import dataclass

from errors import LogicParserError, LogicRuntimeError, LogicSyntaxError
from executor import Executor
from lexer import Lexer
from parser import Parser


@dataclass
class RuntimeOptions:
    tokens: bool = False
    ast: bool = False
    debug: bool = False
    filename: str = "test.lgc"


def parse_arguments() -> RuntimeOptions:
    parser = argparse.ArgumentParser(
        description="Run Logic Lang source files with optional debugging output."
    )
    parser.add_argument("--tokens", action="store_true", help="Print tokens from the lexer")
    parser.add_argument("--ast", action="store_true", help="Print the parsed AST")
    parser.add_argument("--debug", action="store_true", help="Show execution flow during runtime")
    parser.add_argument("filename", nargs="?", default="test.lgc", help="Logic Lang source file")
    args = parser.parse_args()
    return RuntimeOptions(tokens=args.tokens, ast=args.ast, debug=args.debug, filename=args.filename)


def run_file(options: RuntimeOptions):
    try:
        with open(options.filename, "r") as file_handle:
            source_code = file_handle.read()
    except FileNotFoundError:
        print(f"Logic Runtime Error:\nFile: {options.filename}\nMessage: File not found", file=sys.stderr)
        sys.exit(1)

    lexer = Lexer(source_code, filename=options.filename)
    tokens = lexer.tokenize()

    if options.tokens:
        print("Lexer Tokens:")
        for token in tokens:
            print(token)
        print()

    parser = Parser(tokens, filename=options.filename)
    ast = parser.parse()

    if options.ast:
        print("Parsed AST:")
        print(ast)
        print()

    executor = Executor(debug=options.debug)
    executor.execute(ast, filename=options.filename)


def main():
    options = parse_arguments()
    try:
        run_file(options)
    except LogicSyntaxError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    except LogicParserError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    except LogicRuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Execution interrupted by user.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()