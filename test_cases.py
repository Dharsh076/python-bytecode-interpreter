import unittest
from byterun_interpreter import VirtualMachine

class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.vm = VirtualMachine()

    def test_conditional(self):
        def cond_test():
            x = 2
            if x > 0:
                return "positive"
            else:
                return "non-positive"
        self.assertEqual(self.vm.run_code(cond_test.__code__), "positive")

    def test_while_loop(self):
        def while_test():
            x = 0
            while x < 3:
                x += 1
            return x
        self.assertEqual(self.vm.run_code(while_test.__code__), 3)

    def test_for_loop(self):
        def for_test():
            total = 0
            for i in range(3):
                total += i
            return total
        self.assertEqual(self.vm.run_code(for_test.__code__), 3)

    def test_exception(self):
        def exception_test():
            try:
                1 / 0
            except ZeroDivisionError:
                return "handled"
        self.assertEqual(self.vm.run_code(exception_test.__code__), "handled")

if __name__ == '__main__':
    unittest.main()