import dis
import types

class Frame:
    def __init__(self, code, globals=None, locals=None, prev_frame=None):
        self.code = code
        self.globals = globals or {}
        self.locals = locals or {}
        self.stack = []
        self.last_instruction = 0
        self.block_stack = []
        self.prev_frame = prev_frame
        self.builtins = globals.get('__builtins__', __builtins__)

class Block:
    def __init__(self, type, handler, level):
        self.type = type
        self.handler = handler
        self.level = level

class VirtualMachineError(Exception):
    pass

class VirtualMachine:
    def __init__(self):
        self.frames = []
        self.frame = None
        self.return_value = None
        self.exception = None

    def run_code(self, code, globals=None, locals=None):
        frame = self.make_frame(code, globals, locals)
        self.run_frame(frame)
        return self.return_value

    def make_frame(self, code, globals=None, locals=None):
        globals = globals or {}
        globals['__builtins__'] = __builtins__
        locals = locals or globals
        frame = Frame(code, globals, locals, self.frame)
        return frame

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        self.frame = self.frames[-1] if self.frames else None

    def top(self):
        return self.frame.stack[-1]

    def pop(self):
        return self.frame.stack.pop()

    def push(self, *vals):
        self.frame.stack.extend(vals)

    def jump(self, jump):
        self.frame.last_instruction = jump

    def parse_byte_and_args(self):
        f = self.frame
        byte_code = f.code.co_code
        i = f.last_instruction
        opoffset = i
        opcode = byte_code[i]
        f.last_instruction += 1
        arg = None
        if opcode >= dis.HAVE_ARGUMENT:
            arg = byte_code[f.last_instruction] + (byte_code[f.last_instruction + 1] << 8)
            f.last_instruction += 2
        return opoffset, opcode, arg

    def dispatch(self, opcode, arg):
        byte_name = dis.opname[opcode]
        if hasattr(self, f'op_{byte_name}'):
            fn = getattr(self, f'op_{byte_name}')
        else:
            raise VirtualMachineError(f"Unsupported opcode: {byte_name}")
        fn(arg)

    def run_frame(self, frame):
        self.push_frame(frame)
        while True:
            try:
                opoffset, opcode, arg = self.parse_byte_and_args()
                self.dispatch(opcode, arg)
            except StopIteration:
                break
            except Exception as e:
                self.handle_exception(e)
        self.pop_frame()

    def handle_exception(self, e):
        block = None
        while self.frame.block_stack:
            block = self.frame.block_stack.pop()
            if block.type == 'except-handler':
                while len(self.frame.stack) > block.level:
                    self.pop()
                self.push(type(e), e, None)
                self.jump(block.handler)
                return
        raise e

    def op_LOAD_CONST(self, arg):
        val = self.frame.code.co_consts[arg]
        self.push(val)

    def op_POP_TOP(self, arg):
        self.pop()

    def op_LOAD_NAME(self, arg):
        name = self.frame.code.co_names[arg]
        if name in self.frame.locals:
            val = self.frame.locals[name]
        elif name in self.frame.globals:
            val = self.frame.globals[name]
        elif name in self.frame.builtins:
            val = self.frame.builtins[name]
        else:
            raise NameError(f"name '{name}' is not defined")
        self.push(val)

    def op_STORE_NAME(self, arg):
        name = self.frame.code.co_names[arg]
        self.frame.locals[name] = self.pop()

    def op_LOAD_FAST(self, arg):
        name = self.frame.code.co_varnames[arg]
        self.push(self.frame.locals[name])

    def op_STORE_FAST(self, arg):
        name = self.frame.code.co_varnames[arg]
        self.frame.locals[name] = self.pop()

    def op_COMPARE_OP(self, arg):
        right = self.pop()
        left = self.pop()
        result = None
        ops = ['<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is', 'is not', 'exception match', 'BAD']
        op = ops[arg]
        if op == '<': result = left < right
        elif op == '<=': result = left <= right
        elif op == '==': result = left == right
        elif op == '!=': result = left != right
        elif op == '>': result = left > right
        elif op == '>=': result = left >= right
        elif op == 'in': result = left in right
        elif op == 'not in': result = left not in right
        elif op == 'is': result = left is right
        elif op == 'is not': result = left is not right
        elif op == 'exception match': result = issubclass(left, right)
        self.push(result)

    def op_POP_JUMP_IF_FALSE(self, arg):
        val = self.pop()
        if not val:
            self.jump(arg)

    def op_JUMP_FORWARD(self, arg):
        self.jump(self.frame.last_instruction + arg)

    def op_JUMP_ABSOLUTE(self, arg):
        self.jump(arg)

    def op_SETUP_LOOP(self, arg):
        self.frame.block_stack.append(Block('loop', arg, len(self.frame.stack)))

    def op_BREAK_LOOP(self, arg):
        while self.frame.block_stack:
            block = self.frame.block_stack.pop()
            if block.type == 'loop':
                while len(self.frame.stack) > block.level:
                    self.pop()
                self.jump(block.handler)
                return
        raise VirtualMachineError("No loop block found")

    def op_SETUP_EXCEPT(self, arg):
        self.frame.block_stack.append(Block('except-handler', arg, len(self.frame.stack)))

    def op_RAISE_VARARGS(self, arg):
        if arg == 1:
            exc = self.pop()
            raise exc
        elif arg == 2:
            exc = self.pop()
            val = self.pop()
            raise exc(val)

    def op_CALL_FUNCTION(self, arg):
        args = [self.pop() for _ in range(arg)]
        func = self.pop()
        retval = func(*reversed(args))
        self.push(retval)

    def op_RETURN_VALUE(self, arg):
        self.return_value = self.pop()
        raise StopIteration()

    def op_BUILD_LIST(self, arg):
        items = [self.pop() for _ in range(arg)]
        self.push(list(reversed(items)))

    def op_LOAD_GLOBAL(self, arg):
        name = self.frame.code.co_names[arg]
        if name in self.frame.globals:
            val = self.frame.globals[name]
        elif name in self.frame.builtins:
            val = self.frame.builtins[name]
        else:
            raise NameError(f"name '{name}' is not defined")
        self.push(val)

    def op_GET_ITER(self, arg):
        self.push(iter(self.pop()))

    def op_FOR_ITER(self, arg):
        iter_obj = self.top()
        try:
            val = next(iter_obj)
            self.push(val)
        except StopIteration:
            self.pop()
            self.jump(arg)

    def op_SETUP_FINALLY(self, arg):
        self.frame.block_stack.append(Block('finally', arg, len(self.frame.stack)))

    def op_END_FINALLY(self, arg):
        pass
