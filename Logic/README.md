# Logic Lang

Logic Lang is a beginner-friendly interpreted programming language built in pure Python. It is designed to feel high-level while keeping a lightweight structure and expandable architecture.

## Features

- Simple `.lgc` syntax
- Clean lexer, parser, and executor modules
- Variables, functions, conditionals, and loops
- Built-in `print`, `input`, `len`, `type`, `time`, `random`, and `clear`
- Debug options for tokens, AST, and execution flow
- Module import support for `*.lgc` files
- Expandable architecture for future compiler, VM, IDE, and OS integration

## Syntax Example

```lgc
import main

main {
    let x = 5;
    let y = 10;

    print("x + y =", x + y);

    if (x < y) {
        print("x is less than y");
    }

    for (i : 1, 6) {
        print("Loop:", i);
    }
}
```

## Run Logic Lang

```bash
python3 main.py test.lgc
```

### Debug modes

```bash
python3 main.py --tokens test.lgc
python3 main.py --ast test.lgc
python3 main.py --debug test.lgc
```

## Module imports

Logic Lang can load external files from the current directory or the `std/` folder:

```lgc
import math
import utils

main {
    print(square(3));
    greet("Logic");
}
```

## Project Structure

```
Logic/
├── main.py
├── lexer.py
├── parser.py
├── executor.py
├── builtins.py
├── logic_builtins.py
├── errors.py
├── compiler.py
├── vm.py
├── module_loader.py
├── tokens.py
├── test.lgc
└── std/
    ├── main.lgc
    ├── math.lgc
    └── utils.lgc
```

## Future Roadmap

- Expand imports into namespaced modules
- Add classes and object support
- Build a bytecode compiler and VM
- Create a Logic Studio IDE
- Add a package manager and OS-level integration
- Support AI-assisted language tools

## Notes

Logic Lang is intentionally lightweight and beginner-friendly. The architecture is designed so the language can grow without losing clarity.
