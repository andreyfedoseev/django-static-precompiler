from django.core import management
from mock import patch, MagicMock
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.models import Dependency
from static_precompiler.settings import OUTPUT_DIR, ROOT
import os
import shutil
import unittest


class BaseCompilerTestCase(unittest.TestCase):

    def setUp(self):
        from django.conf import settings as django_settings
        self.django_settings = django_settings

        output_dir = os.path.join(self.django_settings.STATIC_ROOT, OUTPUT_DIR)

        # Remove the output directory if it exists to start from scratch
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        management.call_command('syncdb', interactive=False, verbosity=0)

    def tearDown(self):
        output_dir = os.path.join(self.django_settings.STATIC_ROOT, OUTPUT_DIR)

        # Remove the output directory
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        management.call_command('flush', interactive=False, verbosity=0)

    def test_is_supported(self):
        compiler = BaseCompiler()
        self.assertRaises(
            NotImplementedError,
            lambda: compiler.is_supported("dummy.coffee")
        )

    def test_get_output_filename(self):
        compiler = BaseCompiler()
        self.assertRaises(
            NotImplementedError,
            lambda: compiler.get_output_filename("dummy.coffee")
        )

    def test_get_full_source_path(self):

        compiler = BaseCompiler()

        root = os.path.dirname(__file__)

        self.assertEqual(
            compiler.get_full_source_path("scripts/test.coffee"),
            os.path.join(root, "static", "scripts", "test.coffee"),
        )

        # Source file doesn't exist
        self.assertRaises(
            ValueError,
            lambda: compiler.get_full_source_path("scripts/does-not-exist.coffee")
        )

        self.assertEqual(
            compiler.get_full_source_path("another_test.coffee"),
            os.path.normpath(
                os.path.join(
                    root,
                    "staticfiles_dir",
                    "another_test.coffee"
                )
            )
        )

        self.assertEqual(
            compiler.get_full_source_path("prefix/another_test.coffee"),
            os.path.normpath(
                os.path.join(
                    root,
                    "staticfiles_dir_with_prefix",
                    "another_test.coffee"
                )
            )
        )

    def test_get_output_path(self):
        compiler = BaseCompiler()
        compiler.get_output_filename = MagicMock(
            side_effect=lambda source_path: source_path.replace(".coffee", ".js")
        )
        self.assertEqual(
            compiler.get_output_path("scripts/test.coffee"),
            OUTPUT_DIR + "/scripts/test.js"
        )

    def test_get_full_output_path(self):
        compiler = BaseCompiler()
        compiler.get_output_path = MagicMock(
            return_value=OUTPUT_DIR + "/dummy.js"
        )
        self.assertEqual(
            compiler.get_full_output_path("dummy.coffee"),
            os.path.join(ROOT, OUTPUT_DIR, "dummy.js")
        )

    def test_get_source_mtime(self):
        compiler = BaseCompiler()
        compiler.get_full_source_path = MagicMock(return_value="dummy.coffee")
        with patch("static_precompiler.compilers.base.get_mtime") as mocked_get_mtime:
            mocked_get_mtime.return_value = 1
            self.assertEqual(compiler.get_source_mtime("dummy.coffee"), 1)
            mocked_get_mtime.assert_called_with("dummy.coffee")
            #noinspection PyUnresolvedReferences
            compiler.get_full_source_path.assert_called_with("dummy.coffee")

    def test_get_output_mtime(self):
        compiler = BaseCompiler()
        compiler.get_full_output_path = MagicMock(return_value="dummy.js")
        with patch("os.path.exists") as mocked_os_path_exists:
            mocked_os_path_exists.return_value = False
            self.assertEqual(compiler.get_output_mtime("dummy.coffee"), None)
            mocked_os_path_exists.assert_called_with("dummy.js")
            mocked_os_path_exists.return_value = True
            with patch("static_precompiler.compilers.base.get_mtime") as mocked_get_mtime:
                mocked_get_mtime.return_value = 1
                self.assertEqual(compiler.get_output_mtime("dummy.coffee"), 1)
                mocked_get_mtime.assert_called_with("dummy.js")

    def test_should_compile(self):
        compiler = BaseCompiler()
        compiler.get_source_mtime = MagicMock()
        compiler.get_output_mtime = MagicMock()
        compiler.get_dependencies = MagicMock(return_value=["B", "C"])
        mtimes = dict(
            A=1,
            B=3,
            C=5,
        )
        compiler.get_source_mtime.side_effect = lambda x: mtimes[x]

        compiler.get_output_mtime.return_value = None
        self.assertTrue(compiler.should_compile("A"))

        compiler.supports_dependencies = True

        compiler.get_output_mtime.return_value = 6
        self.assertFalse(compiler.should_compile("A"))

        compiler.get_output_mtime.return_value = 5
        self.assertTrue(compiler.should_compile("A"))

        compiler.get_output_mtime.return_value = 4
        self.assertTrue(compiler.should_compile("A"))

        compiler.get_output_mtime.return_value = 2
        self.assertTrue(compiler.should_compile("A"))

        compiler.supports_dependencies = False

        compiler.get_output_mtime.return_value = 2
        self.assertFalse(compiler.should_compile("A"))

        compiler.get_output_mtime.return_value = 1
        self.assertTrue(compiler.should_compile("A"))

        compiler.get_output_mtime.return_value = 0
        self.assertTrue(compiler.should_compile("A"))

        compiler.get_source_mtime.reset_mock()
        with patch("static_precompiler.compilers.base.DISABLE_AUTO_COMPILE"):
            self.assertFalse(compiler.should_compile("A"))
            self.assertFalse(compiler.get_source_mtime.called)

    def test_get_source(self):
        compiler = BaseCompiler()
        self.assertEqual(
            compiler.get_source("scripts/test.coffee"),
            'console.log "Hello, World!"'
        )

    def test_write_output(self):
        compiler = BaseCompiler()
        output_path = os.path.join(ROOT, OUTPUT_DIR, "dummy.js")
        self.assertFalse(os.path.exists(output_path))
        compiler.get_full_output_path = MagicMock(return_value=output_path)
        compiler.write_output("compiled", "dummy.coffee")
        self.assertTrue(os.path.exists(output_path))
        with open(output_path) as output:
            self.assertEqual(output.read(), "compiled")

    def test_compile_source(self):
        compiler = BaseCompiler()
        self.assertRaises(
            NotImplementedError,
            lambda: compiler.compile_source("source")
        )

    def test_postprocess(self):
        compiler = BaseCompiler()
        self.assertEqual(compiler.postprocess("compiled", "dummy.coffee"), "compiled")

    #noinspection PyUnresolvedReferences
    def test_compile(self):
        compiler = BaseCompiler()
        compiler.is_supported = MagicMock()
        compiler.should_compile = MagicMock()
        compiler.compile_file = MagicMock(return_value="compiled")
        compiler.write_output = MagicMock()
        compiler.get_output_path = MagicMock(return_value="dummy.js")
        compiler.postprocess = MagicMock(
            side_effect=lambda compiled, source_path: compiled
        )
        compiler.update_dependencies = MagicMock()
        compiler.find_dependencies = MagicMock(return_value=["A", "B"])

        compiler.is_supported.return_value = False
        self.assertRaises(ValueError, lambda: compiler.compile("dummy.coffee"))

        self.assertEqual(compiler.compile_file.call_count, 0)
        self.assertEqual(compiler.postprocess.call_count, 0)
        self.assertEqual(compiler.write_output.call_count, 0)

        compiler.is_supported.return_value = True
        compiler.should_compile.return_value = False
        self.assertEqual(compiler.compile("dummy.coffee"), "dummy.js")

        self.assertEqual(compiler.compile_file.call_count, 0)
        self.assertEqual(compiler.postprocess.call_count, 0)
        self.assertEqual(compiler.write_output.call_count, 0)

        compiler.should_compile.return_value = True
        self.assertEqual(compiler.compile("dummy.coffee"), "dummy.js")

        self.assertEqual(compiler.compile_file.call_count, 1)
        compiler.compile_file.assert_called_with("dummy.coffee")

        self.assertEqual(compiler.postprocess.call_count, 1)
        compiler.postprocess.assert_called_with("compiled", "dummy.coffee")

        self.assertEqual(compiler.write_output.call_count, 1)
        compiler.write_output.assert_called_with("compiled", "dummy.coffee")

        self.assertEqual(compiler.update_dependencies.call_count, 0)

        compiler.supports_dependencies = True
        compiler.compile("dummy.coffee")
        compiler.find_dependencies.assert_called_with("dummy.coffee")
        compiler.update_dependencies.assert_called_with("dummy.coffee", ["A", "B"])

    def test_compile_lazy(self):
        compiler = BaseCompiler()
        compiler.compile = MagicMock()
        compiler.compile.return_value = "dummy.js"

        lazy_compiled = compiler.compile_lazy("dummy.coffee")

        # noinspection PyUnresolvedReferences
        self.assertEqual(compiler.compile.call_count, 0)

        self.assertEqual(str(lazy_compiled), "dummy.js")

        # noinspection PyUnresolvedReferences
        self.assertEqual(compiler.compile.call_count, 1)
        # noinspection PyUnresolvedReferences
        compiler.compile.assert_called_with("dummy.coffee")

    def test_find_dependencies(self):
        compiler = BaseCompiler()
        self.assertRaises(
            NotImplementedError,
            lambda: compiler.find_dependencies("dummy.coffee")
        )

    def test_get_dependencies(self):
        compiler = BaseCompiler()
        self.assertFalse(Dependency.objects.exists())

        self.assertEqual(
            compiler.get_dependencies("spam.scss"),
            [],
        )

        Dependency.objects.create(
            source="spam.scss",
            depends_on="ham.scss"
        )
        Dependency.objects.create(
            source="spam.scss",
            depends_on="eggs.scss"
        )

        self.assertEqual(
            compiler.get_dependencies("spam.scss"),
            ["eggs.scss", "ham.scss"],
        )

    def test_get_dependents(self):
        compiler = BaseCompiler()
        self.assertFalse(Dependency.objects.exists())

        self.assertEqual(
            compiler.get_dependents("spam.scss"),
            [],
        )

        Dependency.objects.create(
            source="ham.scss",
            depends_on="spam.scss"
        )
        Dependency.objects.create(
            source="eggs.scss",
            depends_on="spam.scss"
        )

        self.assertEqual(
            compiler.get_dependents("spam.scss"),
            ["eggs.scss", "ham.scss"],
        )

    def test_update_dependencies(self):
        compiler = BaseCompiler()

        self.assertFalse(Dependency.objects.exists())

        compiler.update_dependencies("A", ["B", "C"])
        self.assertEqual(
            sorted(Dependency.objects.values_list("source", "depends_on")),
            [("A", "B"), ("A", "C")]
        )

        compiler.update_dependencies("A", ["B", "C", "D"])
        self.assertEqual(
            sorted(Dependency.objects.values_list("source", "depends_on")),
            [("A", "B"), ("A", "C"), ("A", "D")]
        )

        compiler.update_dependencies("A", ["E"])
        self.assertEqual(
            sorted(Dependency.objects.values_list("source", "depends_on")),
            [("A", "E")]
        )

        compiler.update_dependencies("B", ["C"])
        self.assertEqual(
            sorted(Dependency.objects.values_list("source", "depends_on")),
            [("A", "E"), ("B", "C")]
        )

        compiler.update_dependencies("A", [])
        self.assertEqual(
            sorted(Dependency.objects.values_list("source", "depends_on")),
            [("B", "C")]
        )


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(BaseCompilerTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
