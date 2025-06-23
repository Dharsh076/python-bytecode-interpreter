# 🐍 Python Bytecode Interpreter

A minimal Python bytecode interpreter written in Python, inspired by [Byterun](https://github.com/nedbat/byterun). This project explores how Python executes code under the hood and supports core features like:

- Conditional statements (`if/else`)
- Loops (`while`, `for`)
- Exception handling (`try/except`)
- Function calls and return values

## 📂 Project Structure

```
├── byterun_interpreter.py   # Main interpreter logic
├── test_cases.py            # Unit tests using Python's unittest framework
└── README.md                # Project documentation
```

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/python-bytecode-interpreter.git
cd python-bytecode-interpreter
```

### 2. Run Unit Tests
```bash
python test_cases.py
```

> Output should show `OK` if all interpreter features are working correctly.

## ✅ Features Implemented

- [x] LOAD/STORE operations
- [x] Arithmetic and logic execution
- [x] Conditional branching (`POP_JUMP_IF_FALSE`, etc.)
- [x] Loop control (`FOR_ITER`, `JUMP_ABSOLUTE`, etc.)
- [x] Exception stack handling (`SETUP_EXCEPT`, `RAISE_VARARGS`)
- [x] Basic function calling (`CALL_FUNCTION`)
- [x] List creation and iteration

## 🎯 Why This Project?

This interpreter is an educational tool to help you understand:
- How Python executes bytecode
- Stack-based virtual machines
- Control flow mechanics behind Python’s syntax

## 🧪 Test Coverage

Each of the following Python constructs is covered in `test_cases.py`:

- Conditional expressions
- `while` and `for` loops
- Exception handling
- Return value correctness

## 📚 Inspired By

- Allison Kaptur's chapter in [500 Lines or Less](https://github.com/aosabook/500lines)
- [Byterun](https://github.com/nedbat/byterun)

## 📝 License

This project is open-source and available under the MIT License.