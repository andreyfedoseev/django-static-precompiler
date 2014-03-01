# coding: utf-8
from unittest import main, TestCase
from django.template import Context
from django.template.loader import get_template_from_string
from mock import patch, MagicMock
from static_precompiler.compilers import SASS, SCSS
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.utils import normalize_path, fix_line_breaks
import os


class SCSSTestCase(TestCase):

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
@import "rounded-corners", "text-shadow";
"""
        expected = [
            "foo",
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

    def test_scss_templatetag(self):
        template = get_template_from_string("""{% load scss %}{% scss "dummy.scss" %}""")
        with patch("static_precompiler.templatetags.scss.compiler") as mocked_compiler:
            mocked_compiler.compile = MagicMock(return_value="dummy.css")
            self.assertEqual(
                template.render(Context({})),
                "dummy.css",
            )

    def test_inlinescss_templatetag(self):
        template = get_template_from_string("""{% load scss %}{% inlinescss %}source{% endinlinescss %}""")
        with patch("static_precompiler.templatetags.scss.InlineSCSSNode.compiler") as mocked_compiler:
            mocked_compiler.compile_source = MagicMock(return_value="compiled")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )

    def test_compass(self):
        compiler = SCSS()

        self.assertEqual(
            fix_line_breaks(compiler.compile_file("test-compass.scss")),
            "p {\n  background: url('/static/images/test.png'); }\n"
        )


class SASSTestCase(TestCase):

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
        source = """
@import foo.sass
@import "foo"
@import "foo.css"
@import foo screen
@import "http://foo.com/bar"
@import url(foo)
@import "rounded-corners", text-shadow
"""
        expected = [
            "foo",
            "foo.sass",
            "rounded-corners",
            "text-shadow",
        ]
        self.assertEqual(
            compiler.find_imports(source),
            expected
        )

    def test_sass_templatetag(self):
        template = get_template_from_string("""{% load sass %}{% sass "dummy.sass" %}""")
        with patch("static_precompiler.templatetags.sass.compiler") as mocked_compiler:
            mocked_compiler.compile = MagicMock(return_value="dummy.css")
            self.assertEqual(
                template.render(Context({})),
                "dummy.css",
            )

    def test_inlinesass_templatetag(self):
        template = get_template_from_string("""{% load sass %}{% inlinesass %}source{% endinlinesass %}""")
        with patch("static_precompiler.templatetags.sass.InlineSASSNode.compiler") as mocked_compiler:
            mocked_compiler.compile_source = MagicMock(return_value="compiled")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )


if __name__ == '__main__':
    main()
