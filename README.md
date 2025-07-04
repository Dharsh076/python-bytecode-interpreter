🐍 Python Virtual Machine Interpreter

This project implements a simplified stack-based virtual machine (VM) for executing Python bytecode instructions.
It is inspired by Python's internal ceval.c execution loop and serves as an educational model of how Python code runs.

🚀 Features

Instruction Dispatch using Python's dis module

Frame and Stack Management (just like CPython)

Support for control flow: if, while, for

Function calls, local and global variable access

Arithmetic and comparison operations

Debug Mode with detailed stack and opcode trace

📂 Project Structure

python-interpreter/
├── byterun_interpreter.py  # Core VM logic
├── test_cases.py           # Unit tests and example Python functions
├── README.md               # This file

🧠 Concepts Implemented

Stack-based evaluation

Instruction decoding via dis.get_instructions()

Instruction pointer (manual jumps)

Opcode to function dispatch mapping

Frame stack and variable resolution

✅ Sample Supported Opcodes

LOAD_CONST, LOAD_FAST, STORE_FAST

LOAD_GLOBAL, CALL_FUNCTION

COMPARE_OP, POP_JUMP_IF_FALSE, JUMP_ABSOLUTE

GET_ITER, FOR_ITER, INPLACE_ADD

RETURN_VALUE, BINARY_ADD, BINARY_TRUE_DIVIDE

🧪 Running Tests

python test_cases.py

This will run a series of Python functions (e.g., conditionals, loops) through the VM and compare outputs with native execution.

⚙️ Debug Mode Output

Enabling self.debug = True in the VirtualMachine class shows:

Current instruction and argument

Stack before and after each opcode

Loop jumps and instruction flow

📜 License

MIT License. See LICENSE file.

🧱 Author

Dharshini Vasudevan

🤝 Contributions

PRs are welcome to:

Add more opcode support (e.g., with, try, class)

Improve exception handling

Add logging or visual stack trace UI

📎 References

cpython/ceval.c

500 Lines or Less: A Simple Object Model

dis — Python Bytecode Disassembler

