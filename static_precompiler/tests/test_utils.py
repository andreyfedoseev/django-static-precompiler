from django.core.exceptions import ImproperlyConfigured
from mock import patch, MagicMock
from static_precompiler.compilers import CoffeeScript
from static_precompiler.exceptions import UnsupportedFile, CompilerNotFound
from static_precompiler.utils import get_compilers, get_compiler_by_name, \
    get_compiler_by_path, compile_static, compile_static_lazy
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
            self.assertTrue(CoffeeScript.name in compilers)
            self.assertTrue(isinstance(compilers[CoffeeScript.name], CoffeeScript))

    def test_get_compiler_by_name(self):
        with patch("static_precompiler.utils.get_compilers") as mocked_get_compilers:
            mocked_get_compilers.return_value = {CoffeeScript.name: CoffeeScript()}

            self.assertRaises(CompilerNotFound, get_compiler_by_name, 'non-existing compiler')

            compiler = get_compiler_by_name(CoffeeScript.name)
            self.assertTrue(isinstance(compiler, CoffeeScript))

    def test_get_compiler_by_path(self):
        mocked_coffeescript_compiler = MagicMock()
        mocked_coffeescript_compiler.is_supported.side_effect = lambda source_path: source_path.endswith(".coffee")
        mocked_less_compiler = MagicMock()
        mocked_less_compiler.is_supported.side_effect = lambda source_path: source_path.endswith(".less")
        with patch("static_precompiler.utils.get_compilers") as mocked_get_compilers:
            mocked_get_compilers.return_value = {
                "coffeescript": mocked_coffeescript_compiler,
                "less": mocked_less_compiler,
            }

            self.assertRaises(
                UnsupportedFile,
                get_compiler_by_path,
                "test.sass"
            )

            self.assertTrue(get_compiler_by_path("test.coffee") is mocked_coffeescript_compiler)
            self.assertTrue(get_compiler_by_path("test.less") is mocked_less_compiler)

    def test_compile_static(self):
        mocked_compiler = MagicMock()
        mocked_compiler.compile.return_value = "compiled"
        mocked_compiler.compile_lazy.return_value = "compiled"
        source_filename = "test.coffee"
        with patch("static_precompiler.utils.get_compiler_by_path") as mocked_get_compiler_by_path:
            mocked_get_compiler_by_path.return_value = mocked_compiler
            self.assertEquals(
                compile_static(source_filename),
                "compiled"
            )
            mocked_get_compiler_by_path.assert_called_once_with(source_filename)
            mocked_compiler.compile.assert_called_once_with(source_filename)

            mocked_get_compiler_by_path.reset_mock()
            self.assertEquals(
                compile_static_lazy(source_filename),
                "compiled"
            )
            mocked_get_compiler_by_path.assert_called_once_with(source_filename)
            mocked_compiler.compile_lazy.assert_called_once_with(source_filename)


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(UtilsTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
