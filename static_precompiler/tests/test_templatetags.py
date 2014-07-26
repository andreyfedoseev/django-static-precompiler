from django.template import Context
from django.template.loader import get_template_from_string
from mock import MagicMock, patch
from static_precompiler.templatetags.compile_static import compile_tag
import unittest


class TemplateTagsTestCase(unittest.TestCase):

    def test_compile_tag(self):
        with patch("static_precompiler.templatetags.compile_static.compile_static") as mocked_compile_static:
            mocked_compile_static.return_value = "compiled"
            template = get_template_from_string("""{% load compile_static %}{% compile "source" %}""")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )
            with patch("static_precompiler.templatetags.compile_static.PREPEND_STATIC_URL", True):
                self.assertEqual(
                    template.render(Context({})),
                    "/static/compiled",
                )

        mocked_compiler = MagicMock()
        mocked_compiler.compile.return_value = "compiled"
        self.assertEqual(
            compile_tag("source", mocked_compiler),
            "compiled"
        )
        mocked_compiler.compile.assert_called_with("source")

    @patch("static_precompiler.templatetags.coffeescript.compiler")
    def test_coffeescript_tag(self, mocked_compiler):
        mocked_compiler.compile.return_value = "compiled"
        template = get_template_from_string("""{% load coffeescript %}{% coffeescript "source" %}""")
        self.assertEqual(
            template.render(Context({})),
            "compiled",
        )
        mocked_compiler.compile.assert_called_with("source")

    @patch("static_precompiler.templatetags.coffeescript.InlineCoffeescriptNode.compiler")
    def test_inlinecoffessecript_templatetag(self, mocked_compiler):
        template = get_template_from_string("""{% load coffeescript %}{% inlinecoffeescript %}source{% endinlinecoffeescript %}""")
        mocked_compiler.compile_source = MagicMock(return_value="compiled")
        self.assertEqual(
            template.render(Context({})),
            "compiled",
        )

    @patch("static_precompiler.templatetags.less.compiler")
    def test_less_tag(self, mocked_compiler):
        mocked_compiler.compile.return_value = "compiled"
        template = get_template_from_string("""{% load less %}{% less "source" %}""")
        self.assertEqual(
            template.render(Context({})),
            "compiled",
        )
        mocked_compiler.compile.assert_called_with("source")

    @patch("static_precompiler.templatetags.less.InlineLESSNode.compiler")
    def test_inlineless_templatetag(self, mocked_compiler):
        template = get_template_from_string("""{% load less %}{% inlineless %}source{% endinlineless %}""")
        mocked_compiler.compile_source = MagicMock(return_value="compiled")
        self.assertEqual(
            template.render(Context({})),
            "compiled",
        )

    @patch("static_precompiler.templatetags.sass.compiler")
    def test_sass_tag(self, mocked_compiler):
        mocked_compiler.compile.return_value = "compiled"
        template = get_template_from_string("""{% load sass %}{% sass "source" %}""")
        self.assertEqual(
            template.render(Context({})),
            "compiled",
        )
        mocked_compiler.compile.assert_called_with("source")

    def test_inlinesass_templatetag(self):
        template = get_template_from_string("""{% load sass %}{% inlinesass %}source{% endinlinesass %}""")
        with patch("static_precompiler.templatetags.sass.InlineSASSNode.compiler") as mocked_compiler:
            mocked_compiler.compile_source = MagicMock(return_value="compiled")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )

    @patch("static_precompiler.templatetags.scss.compiler")
    def test_scss_tag(self, mocked_compiler):
        mocked_compiler.compile.return_value = "compiled"
        template = get_template_from_string("""{% load scss %}{% scss "source" %}""")
        self.assertEqual(
            template.render(Context({})),
            "compiled",
        )
        mocked_compiler.compile.assert_called_with("source")

    def test_inlinescss_templatetag(self):
        template = get_template_from_string("""{% load scss %}{% inlinescss %}source{% endinlinescss %}""")
        with patch("static_precompiler.templatetags.scss.InlineSCSSNode.compiler") as mocked_compiler:
            mocked_compiler.compile_source = MagicMock(return_value="compiled")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(TemplateTagsTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
