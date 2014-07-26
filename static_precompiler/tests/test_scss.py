# coding: utf-8
from django.template import Context
from django.template.loader import get_template_from_string
from mock import patch, MagicMock
from static_precompiler.compilers import SASS, SCSS
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.utils import normalize_path, fix_line_breaks
import os
import unittest


class SCSSTestCase(unittest.TestCase):

    def test_is_supported(self):
        compiler = SCSS()
        self.assertEqual(compiler.is_supported("dummy"), False)
        self.assertEqual(compiler.is_supported("dummy.scss"), True)

    def test_get_output_filename(self):
        compiler = SCSS()
        self.assertEqual(compiler.get_output_filename("dummy.scss"), "dummy.css")
        self.assertEqual(
            compiler.get_output_filename("dummy.scss.scss"),
            "dummy.scss.css"
        )

    def test_compile_file(self):
        compiler = SCSS()

        self.assertEqual(
            fix_line_breaks(compiler.compile_file("styles/test.scss")),
            "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"
        )

    def test_compile_source(self):
        compiler = SCSS()

        self.assertEqual(
            fix_line_breaks(compiler.compile_source("p {font-size: 15px; a {color: red;}}")),
            "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"
        )

        self.assertRaises(
            StaticCompilationError,
            lambda: compiler.compile_source('invalid syntax')
        )

        # Test non-ascii
        NON_ASCII = """@charset "UTF-8";
.external_link:first-child:before {
  content: "Zobacz także:";
  background: url(картинка.png); }
"""
        self.assertEqual(
            fix_line_breaks(compiler.compile_source(NON_ASCII)),
            NON_ASCII
        )

    def test_postprocesss(self):
        compiler = SCSS()
        with patch("static_precompiler.compilers.scss.convert_urls") as mocked_convert_urls:
            mocked_convert_urls.return_value = "spam"
            self.assertEqual(compiler.postprocess("ham", "eggs"), "spam")
            mocked_convert_urls.assert_called_with("ham", "eggs")

    def test_parse_import_string(self):
        compiler = SCSS()
        import_string = """"foo, bar" , "foo", url(bar,baz),
         'bar,foo',bar screen, projection"""
        self.assertEqual(
            compiler.parse_import_string(import_string), [
                "bar",
                "bar,foo",
                "foo",
                "foo, bar",
            ]
        )
        import_string = """"foo,bar", url(bar,baz), 'bar,foo',bar screen, projection"""
        self.assertEqual(
            compiler.parse_import_string(import_string), [
                "bar",
                "bar,foo",
                "foo,bar",
            ]
        )
        import_string = """"foo" screen"""
        self.assertEqual(
            compiler.parse_import_string(import_string), [
                "foo",
            ]
        )

    def test_find_imports(self):
        compiler = SCSS()
        source = """
@import "foo.css", ;
@import " ";
@import "foo.scss";
@import "foo";
@import "foo.css";
@import "foo" screen;
@import "http://foo.com/bar";
@import url(foo);
@import "rounded-corners",
        "text-shadow";
@import "compass";
@import "compass.scss";
@import "compass/css3";
@import url(http://fonts.googleapis.com/css?family=Arvo:400,700,400italic,700italic);
@import url("http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,400,700,600,300");
@import "foo,bar", url(bar,baz), 'bar,foo';
"""

        compiler.compass_enabled = MagicMock()
        compiler.compass_enabled.return_value = False

        expected = [
            "bar,foo",
            "compass",
            "compass.scss",
            "compass/css3",
            "foo",
            "foo,bar",
            "foo.scss",
            "rounded-corners",
            "text-shadow",
        ]
        self.assertEqual(
            compiler.find_imports(source),
            expected
        )

        compiler.compass_enabled.return_value = True
        expected = [
            "bar,foo",
            "foo",
            "foo,bar",
            "foo.scss",
            "rounded-corners",
            "text-shadow",
        ]
        self.assertEqual(
            compiler.find_imports(source),
            expected
        )

    def test_locate_imported_file(self):
        compiler = SCSS()
        with patch("os.path.exists") as mocked_os_path_exist:

            root = os.path.dirname(__file__)

            existing_files = set()
            for f in ("A/B.scss", "A/_C.scss", "D.scss"):
                existing_files.add(os.path.join(root, "static", normalize_path(f)))

            mocked_os_path_exist.side_effect = lambda x: x in existing_files

            self.assertEqual(
                compiler.locate_imported_file("A", "B.scss"),
                "A/B.scss"
            )
            self.assertEqual(
                compiler.locate_imported_file("A", "C"),
                "A/_C.scss"
            )
            self.assertEqual(
                compiler.locate_imported_file("E", "../D"),
                "D.scss"
            )
            self.assertEqual(
                compiler.locate_imported_file("E", "../A/B.scss"),
                "A/B.scss"
            )
            self.assertEqual(
                compiler.locate_imported_file("", "D.scss"),
                "D.scss"
            )
            self.assertRaises(
                StaticCompilationError,
                lambda: compiler.locate_imported_file("", "Z.scss")
            )

    def test_find_dependencies(self):
        compiler = SCSS()
        files = {
            "A.scss": "@import 'B/C.scss';",
            "B/C.scss": "@import '../E';",
            "_E.scss": "p {color: red;}",
            "compass-import.scss": '@import "compass"',
        }
        compiler.get_source = MagicMock(side_effect=lambda x: files[x])

        root = os.path.dirname(__file__)

        existing_files = set()
        for f in files:
            existing_files.add(os.path.join(root, "static", normalize_path(f)))

        with patch("os.path.exists") as mocked_os_path_exist:
            mocked_os_path_exist.side_effect = lambda x: x in existing_files

            self.assertEqual(
                compiler.find_dependencies("A.scss"),
                ["B/C.scss", "_E.scss"]
            )
            self.assertEqual(
                compiler.find_dependencies("B/C.scss"),
                ["_E.scss"]
            )
            self.assertEqual(
                compiler.find_dependencies("_E.scss"),
                []
            )

    def test_compass(self):
        compiler = SCSS()

        self.assertEqual(
            fix_line_breaks(compiler.compile_file("test-compass.scss")),
            "p {\n  background: url('/static/images/test.png'); }\n"
        )

    def test_compass_import(self):
        compiler = SCSS()

        with patch.object(compiler, "compass_enabled", return_value=True):
            self.assertEqual(
                fix_line_breaks(compiler.compile_file("styles/test-compass-import.scss")),
                ".round-corners {\n  -webkit-border-radius: 4px 4px;\n  -moz-border-radius: 4px / 4px;\n  border-radius: 4px / 4px; }\n"
            )

        with patch.object(compiler, "compass_enabled", return_value=False):
            self.assertRaises(StaticCompilationError, lambda: compiler.compile_file("styles/test-compass-import.scss"))


class SASSTestCase(unittest.TestCase):

    def test_is_supported(self):
        compiler = SASS()
        self.assertEqual(compiler.is_supported("dummy"), False)
        self.assertEqual(compiler.is_supported("dummy.sass"), True)

    def test_get_output_filename(self):
        compiler = SASS()
        self.assertEqual(compiler.get_output_filename("dummy.sass"), "dummy.css")
        self.assertEqual(
            compiler.get_output_filename("dummy.sass.sass"),
            "dummy.sass.css"
        )

    def test_compile_file(self):
        compiler = SASS()

        self.assertEqual(
            fix_line_breaks(compiler.compile_file("styles/test.sass")),
            "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"
        )

    def test_compile_source(self):
        compiler = SASS()

        self.assertEqual(
            fix_line_breaks(compiler.compile_source("p\n  font-size: 15px")),
            "p {\n  font-size: 15px; }\n"
        )

        self.assertRaises(
            StaticCompilationError,
            lambda: compiler.compile_source('invalid syntax')
        )

    def test_find_imports(self):
        compiler = SASS()
        source = """@import foo.sass
@import "foo.css"
@import foo screen
@import "http://foo.com/bar"
@import url(foo)
@import "rounded-corners", text-shadow
@import "foo,bar", url(bar,baz), 'bar,foo',bar screen, projection"""
        expected = [
            "bar",
            "bar,foo",
            "foo",
            "foo,bar",
            "foo.sass",
            "rounded-corners",
            "text-shadow",
        ]
        self.assertEqual(
            compiler.find_imports(source),
            expected
        )


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(SASSTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(SCSSTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
