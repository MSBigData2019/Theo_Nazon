# coding: utf-8
import unittest

def function_name():
    return None


# Here's our "unit tests".
class SomethingNameTests(unittest.TestCase):
    def testFunctionName(self):
        self.assertEqual(function_name(INPUT VALUE) , EXPECTED OUTPUT)

def main():
    unittest.main()

if __name__ == '__main__':
    main()

# assertEqual() to check for an expected result;
# assertTrue() or assertFalse() to verify a condition;
# assertRaises() to verify that a specific exception gets raised

# The unittest module can be used from the command line to run tests from modules, classes or even individual test methods:

# python -m unittest test_module1 test_module2
# python -m unittest test_module.TestClass
# python -m unittest test_module.TestClass.test_method
# You can pass in a list with any combination of module names, and fully qualified class or method names.

# Test modules can be specified by file path as well:

# python -m unittest tests/test_something.py
# This allows you to use the shell filename completion to specify the test module. The file specified must still be importable as a module. The path is converted to a module name by removing the ‘.py’ and converting path separators into ‘.’. If you want to execute a test file that isn’t importable as a module you should execute the file directly instead.

# You can run tests with more detail (higher verbosity) by passing in the -v flag:

# python -m unittest -v test_module
# When executed without arguments Test Discovery is started:

# python -m unittest
# For a list of all the command-line options:

# python -m unittest -h
