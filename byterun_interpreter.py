import dis

class VirtualMachineError(Exception):
    """Raised when the virtual machine encounters an unsupported or unexpected condition."""
    pass

class Frame:
    """
    Represents a single call frame in the virtual machine stack.
    Contains the code object, local and global namespaces, and an operand stack.
    """
    def __init__(self, code, globals=None, locals=None, prev_frame=None):
        self.code = code
        self.globals = globals or {}
        self.locals = locals or {}
        self.stack = []
        self.last_instruction = 0
        self.prev_frame = prev_frame

class VirtualMachine:
    """
    A simple stack-based Python virtual machine capable of executing basic Python bytecode.
    Supports arithmetic, control flow, and function calls.
    """
    def __init__(self):
        self.frames = []
        self.frame = None
        self.return_value = None
        self.debug = True  # Toggle this to enable/disable stack trace

    def run_code(self, code, globals=None, locals=None):
        """Execute the given Python code object."""
        frame = Frame(code, globals=globals, locals=locals)
        self.push_frame(frame)

        instructions = list(dis.get_instructions(code))
        i = 0
        try:
            while i < len(instructions):
                instr = instructions[i]
                opname = instr.opname
                argval = instr.argval
                fn = getattr(self, f"op_{opname}", None)
                if not fn:
                    raise VirtualMachineError(f"Unsupported opcode: {opname}")

                if self.debug:
                    print(f"\n--> Executing {opname} {argval}")
                    print(f"    Stack before: {self.frame.stack}")

                if argval is not None:
                    fn(argval)
                else:
                    fn()

                if self.debug:
                    print(f"    Stack after:  {self.frame.stack}")

                # Handle jumps
                if self.frame.last_instruction != 0:
                    for j, ins in enumerate(instructions):
                        if ins.offset == self.frame.last_instruction:
                            i = j
                            self.frame.last_instruction = 0
                            break
                    continue

                i += 1
        except StopIteration:
            pass
        except Exception as e:
            if self.debug:
                print("\n[!] Exception encountered:", e)
            raise e
        finally:
            self.pop_frame()

        return self.return_value

    def push_frame(self, frame):
        """Push a new execution frame onto the VM stack."""
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        """Pop the top execution frame off the VM stack."""
        self.frames.pop()
        self.frame = self.frames[-1] if self.frames else None

    def push(self, *vals):
        """Push values onto the operand stack."""
        self.frame.stack.extend(vals)

    def pop(self):
        """Pop a value from the operand stack."""
        if not self.frame.stack:
            print("[!] Warning: Stack empty on POP")
            return None
        return self.frame.stack.pop()

    def popn(self, n):
        """Pop 'n' values from the operand stack."""
        if n == 0:
            return []
        ret = self.frame.stack[-n:]
        self.frame.stack[-n:] = []
        return ret

    def top(self):
        """Peek at the top value of the operand stack."""
        return self.frame.stack[-1]

    def jump(self, jump_target):
        """Update the instruction pointer to the target offset."""
        self.frame.last_instruction = jump_target

    # ----------------------
    # Opcode Implementations
    # ----------------------

    def op_LOAD_CONST(self, const):
        """Push a constant value onto the stack."""
        self.push(const)

    def op_RETURN_VALUE(self):
        """Return the top value of the stack as the function result."""
        self.return_value = self.pop()
        raise StopIteration

    def op_POP_TOP(self):
        """Remove the top value of the stack."""
        self.pop()

    def op_STORE_NAME(self, name):
        """Pop value and store in locals under the given name."""
        self.frame.locals[name] = self.pop()

    def op_LOAD_NAME(self, name):
        """Load a name from locals or globals."""
        val = self.frame.locals.get(name, self.frame.globals.get(name, None))
        if val is None:
            raise NameError(f"name '{name}' is not defined")
        self.push(val)

    def op_LOAD_FAST(self, name):
        """Load a local variable."""
        self.push(self.frame.locals[name])

    def op_STORE_FAST(self, name):
        """Store a local variable."""
        self.frame.locals[name] = self.pop()

    def op_LOAD_GLOBAL(self, name):
        """Load a global variable or built-in."""
        val = self.frame.globals.get(name)
        if val is None:
            val = __builtins__[name]
        self.push(val)

    def op_BINARY_ADD(self):
        """Pop two values and push their sum."""
        b = self.pop()
        a = self.pop()
        self.push(a + b)

    def op_INPLACE_ADD(self):
        """Perform in-place addition on top two values."""
        b = self.pop()
        a = self.pop()
        self.push(a + b)
        if self.debug:
            print("INPLACE_ADD executed")

    def op_CALL_FUNCTION(self, argc):
        """Call a function with argc arguments."""
        args = self.popn(argc)
        func = self.pop()
        self.push(func(*args))

    def op_COMPARE_OP(self, op):
        """Compare top two stack values with the given operation."""
        b = self.pop()
        a = self.pop()
        if op == '<':
            self.push(a < b)
        elif op == '>':
            self.push(a > b)
        elif op == '==':
            self.push(a == b)
        elif op == '!=':
            self.push(a != b)
        elif op == '<=':
            self.push(a <= b)
        elif op == '>=':
            self.push(a >= b)
        else:
            raise VirtualMachineError(f"Unsupported compare op: {op}")

    def op_POP_JUMP_IF_FALSE(self, jump_target):
        """Jump to target if top of stack is False."""
        value = self.pop()
        if not value:
            self.jump(jump_target)

    def op_JUMP_FORWARD(self, target):
        """Unconditionally jump to an instruction offset."""
        self.frame.last_instruction = target

    def op_JUMP_ABSOLUTE(self, jump_target):
        """Unconditional absolute jump to bytecode offset."""
        self.jump(jump_target)

    def op_GET_ITER(self):
        """Get iterator from iterable and push it onto the stack."""
        obj = self.pop()
        self.push(iter(obj))

    def op_FOR_ITER(self, jump):
        """Iterate through iterator; jump on StopIteration."""
        if self.debug:
            print("FOR_ITER executed")
        try:
            iter_obj = self.top()
            val = next(iter_obj)
            self.push(val)
        except StopIteration:
            self.pop()
            self.jump(jump)

    def op_SETUP_LOOP(self, dest):
        """Setup loop block (no-op for now)."""
        pass

    def op_SETUP_EXCEPT(self, dest):
        """Setup exception block (no-op for now)."""
        pass

    def op_SETUP_FINALLY(self, dest):
        """Setup finally block (no-op for now)."""
        pass

    def op_RAISE_VARARGS(self, argc):
        """Raise exceptions with one or two arguments."""
        if argc == 1:
            raise self.pop()
        elif argc == 2:
            exc = self.pop()
            cause = self.pop()
            raise exc from cause
        else:
            raise VirtualMachineError("Unsupported RAISE_VARARGS argc")

    def op_END_FINALLY(self):
        """End of a finally block (no-op for now)."""
        pass

    def op_BINARY_TRUE_DIVIDE(self):
        """Perform true division on top two values."""
        b = self.pop()
        a = self.pop()
        self.push(a / b)
