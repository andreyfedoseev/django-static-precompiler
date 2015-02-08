# coding: utf-8
from static_precompiler.compilers.es6 import ES6Script
from static_precompiler.exceptions import StaticCompilationError
import unittest


class ES6ScriptTestCase(unittest.TestCase):

    @staticmethod
    def clean_javascript(js):
        """ Remove comments and all blank lines. """
        return "\n".join(
            line for line in js.split("\n") if line.strip() and not line.startswith("//")
        )

    def test_compile_file(self):
        compiler = ES6Script()

        self.assertEqual(
            self.clean_javascript(compiler.compile_file("scripts/test.es6")),
            """"use strict";\nconsole.log("Hello, World!");"""
        )

    def test_compile_source(self):
        compiler = ES6Script()

        self.assertEqual(
            self.clean_javascript(compiler.compile_source('console.log("Hello, World!");')),
            """"use strict";\nconsole.log("Hello, World!");"""
        )

        self.assertRaises(
            StaticCompilationError,
            lambda: compiler.compile_source('console.log "Hello, World!')
        )

        # Test non-ascii
        self.assertEqual(
            self.clean_javascript(compiler.compile_source('console.log("Привет, Мир!");')),
            """"use strict";\nconsole.log("Привет, Мир!");"""
        )


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(ES6ScriptTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
