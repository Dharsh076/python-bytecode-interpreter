import dis

class VirtualMachineError(Exception):
    pass

class Frame:
    def __init__(self, code, globals=None, locals=None, prev_frame=None):
        self.code = code
        self.globals = globals or {}
        self.locals = locals or {}
        self.stack = []
        self.last_instruction = 0
        self.prev_frame = prev_frame

class VirtualMachine:
    def __init__(self):
        self.frames = []
        self.frame = None
        self.return_value = None
        self.running = False

    def run_code(self, code, globals=None, locals=None):
        frame = Frame(code, globals=globals, locals=locals)
        self.push_frame(frame)

        instructions = list(dis.get_instructions(code))
        i = 0
        self.running = True

        try:
            while i < len(instructions) and self.running:
                instr = instructions[i]
                opname = instr.opname
                argval = instr.argval
                fn = getattr(self, f"op_{opname}", None)
                if not fn:
                    raise VirtualMachineError(f"Unsupported opcode: {opname}")
                if argval is not None:
                    fn(argval)
                else:
                    fn()

                # Check for manual jump
                if self.frame.last_instruction != 0:
                    for j, ins in enumerate(instructions):
                        if ins.offset == self.frame.last_instruction:
                            i = j
                            self.frame.last_instruction = 0
                            break
                    continue

                i += 1
        except Exception as e:
            raise e
        finally:
            self.pop_frame()

        return self.return_value

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        self.frame = self.frames[-1] if self.frames else None

    def push(self, *vals):
        self.frame.stack.extend(vals)

    def pop(self):
        if not self.frame.stack:
            print("[!] Warning: Stack empty on POP")
            return None
        return self.frame.stack.pop()

    def popn(self, n):
        if n == 0:
            return []
        ret = self.frame.stack[-n:]
        self.frame.stack[-n:] = []
        return ret

    def top(self):
        return self.frame.stack[-1]

    def jump(self, jump_target):
        self.frame.last_instruction = jump_target

    # -------- Opcodes -------- #
    def op_LOAD_CONST(self, const):
        self.push(const)

    def op_RETURN_VALUE(self):
        self.return_value = self.pop()
        self.running = False  # replaced raise StopIteration

    def op_POP_TOP(self):
        self.pop()

    def op_STORE_NAME(self, name):
        self.frame.locals[name] = self.pop()

    def op_LOAD_NAME(self, name):
        val = self.frame.locals.get(name, self.frame.globals.get(name, None))
        if val is None:
            raise NameError(f"name '{name}' is not defined")
        self.push(val)

    def op_LOAD_FAST(self, name):
        self.push(self.frame.locals[name])

    def op_STORE_FAST(self, name):
        self.frame.locals[name] = self.pop()

    def op_LOAD_GLOBAL(self, name):
        val = self.frame.globals.get(name)
        if val is None:
            val = __builtins__[name]
        self.push(val)

    def op_BINARY_ADD(self):
        b = self.pop()
        a = self.pop()
        self.push(a + b)

    def op_INPLACE_ADD(self):
        b = self.pop()
        a = self.pop()
        self.push(a + b)
        print("INPLACE_ADD executed")

    def op_CALL_FUNCTION(self, argc):
        args = self.popn(argc)
        func = self.pop()
        self.push(func(*args))

    def op_COMPARE_OP(self, op):
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
        value = self.pop()
        if not value:
            self.jump(jump_target)

    def op_JUMP_FORWARD(self, target):
        self.frame.last_instruction = target

    def op_JUMP_ABSOLUTE(self, jump_target):
        self.jump(jump_target)

    def op_GET_ITER(self):
        obj = self.pop()
        self.push(iter(obj))

    def op_FOR_ITER(self, jump):
        print("FOR_ITER executed")
        try:
            iter_obj = self.top()
            val = next(iter_obj)
            self.push(val)
        except StopIteration:
            self.pop()
            self.jump(jump)

    def op_SETUP_LOOP(self, dest):
        pass

    def op_SETUP_EXCEPT(self, dest):
        pass

    def op_SETUP_FINALLY(self, dest):
        pass

    def op_RAISE_VARARGS(self, argc):
        if argc == 1:
            raise self.pop()
        elif argc == 2:
            exc = self.pop()
            cause = self.pop()
            raise exc from cause
        else:
            raise VirtualMachineError("Unsupported RAISE_VARARGS argc")

    def op_END_FINALLY(self):
        pass

    def op_BINARY_TRUE_DIVIDE(self):
        b = self.pop()
        a = self.pop()
        self.push(a / b)
