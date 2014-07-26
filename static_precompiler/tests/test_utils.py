from django.core.exceptions import ImproperlyConfigured
from mock import patch, MagicMock
from static_precompiler.compilers import CoffeeScript
from static_precompiler.exceptions import UnsupportedFile
from static_precompiler.utils import get_compilers, compile_static, compile_static_lazy
import unittest


class UtilsTestCase(unittest.TestCase):

    def test_get_compilers(self):
        with patch("static_precompiler.utils.COMPILERS", ["invalid_classpath"]):
            self.assertRaises(ImproperlyConfigured, get_compilers)

        with patch("static_precompiler.utils.COMPILERS", ["non_existing_module.ClassName"]):
            self.assertRaises(ImproperlyConfigured, get_compilers)

        with patch("static_precompiler.utils.COMPILERS", ["static_precompiler.NonExistingClass"]):
            self.assertRaises(ImproperlyConfigured, get_compilers)

        with patch("static_precompiler.utils.COMPILERS", ["static_precompiler.compilers.CoffeeScript"]):
            compilers = get_compilers()
            self.assertEqual(len(compilers), 1)
            self.assertTrue(isinstance(compilers[0], CoffeeScript))

    def test_compile_static(self):
        mocked_coffeescript_compiler = MagicMock()
        mocked_coffeescript_compiler.is_supported.side_effect = lambda source_path: source_path.endswith(".coffee")
        mocked_coffeescript_compiler.compile.return_value = "compiled coffeescript"
        mocked_less_compiler = MagicMock()
        mocked_less_compiler.is_supported.side_effect = lambda source_path: source_path.endswith(".less")
        mocked_less_compiler.compile.return_value = "compiled less"

        with patch("static_precompiler.utils.get_compilers") as mocked_get_compilers:
            mocked_get_compilers.return_value = [
                mocked_coffeescript_compiler,
                mocked_less_compiler
            ]
            self.assertEquals(
                compile_static("test.coffee"),
                "compiled coffeescript"
            )
            self.assertEquals(
                compile_static("test.less"),
                "compiled less"
            )
            self.assertRaises(
                UnsupportedFile,
                lambda: compile_static("test.sass")
            )

    def test_compile_static_lazy(self):
        mocked_compiler = MagicMock()
        mocked_compiler.compile_lazy.return_value = "compiled"

        with patch("static_precompiler.utils.get_compilers") as mocked_get_compilers:
            mocked_get_compilers.return_value = [
                mocked_compiler,
            ]
            self.assertEquals(
                compile_static_lazy("source"),
                "compiled"
            )
            mocked_compiler.compile_lazy.assert_called_with("source")


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(UtilsTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
