import unittest
from byterun_interpreter import VirtualMachine

vm = VirtualMachine()

def sample():
    return 42

def cond_test():
    x = 10
    if x > 0:
        return "positive"
    else:
        return "negative"

def while_test():
    x = 0
    while x < 3:
        x += 1
    return x

def for_test():
    total = 0
    for i in range(3):
        total += 1
    return total

def exception_test():
    try:
        1 / 0
    except ZeroDivisionError:
        return "handled"

class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.vm = VirtualMachine()

    def test_sample(self):
        self.assertEqual(self.vm.run_code(sample.__code__), 42)

    def test_conditional(self):
        self.assertEqual(self.vm.run_code(cond_test.__code__), "positive")

    def test_while_loop(self):
        self.assertEqual(self.vm.run_code(while_test.__code__), 3)

    def test_for_loop(self):
        self.assertEqual(self.vm.run_code(for_test.__code__), 3)
    @unittest.skip("Exception handling not implemented")
    def test_exception(self):
        self.assertEqual(self.vm.run_code(exception_test.__code__), "handled")

if __name__ == "__main__":
    unittest.main()
