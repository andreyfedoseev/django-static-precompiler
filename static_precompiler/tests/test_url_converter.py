# coding: utf-8
from mock import MagicMock
from static_precompiler.utils import URLConverter
import unittest


class URLConverterTestCase(unittest.TestCase):

    def test_convert_url(self):
        converter = URLConverter()
        self.assertEqual(
            converter.convert_url("http://dummy.jpg", "styles/"),
            "http://dummy.jpg"
        )
        self.assertEqual(
            converter.convert_url("https://dummy.jpg", "styles/"),
            "https://dummy.jpg"
        )
        self.assertEqual(
            converter.convert_url("/dummy.jpg", "styles/"),
            "/dummy.jpg"
        )
        self.assertEqual(
            converter.convert_url("data:abc", "styles/"),
            "data:abc"
        )
        self.assertEqual(
            converter.convert_url("dummy.jpg", "styles/"),
            "/static/styles/dummy.jpg"
        )
        self.assertEqual(
            converter.convert_url("./dummy.jpg", "styles/"),
            "/static/styles/dummy.jpg"
        )
        self.assertEqual(
            converter.convert_url("../images/dummy.jpg", "styles/"),
            "/static/images/dummy.jpg"
        )

    def test_convert(self):
        converter = URLConverter()
        converter.convert_url = MagicMock(return_value="spam.jpg")
        self.assertEqual(
            converter.convert("p {\n  background-url: url(ham.jpg);\n}", ""),
            "p {\n  background-url: url('spam.jpg');\n}"
        )
        self.assertEqual(
            converter.convert('p {\n  background-url: url("ham.jpg");\n}', ""),
            "p {\n  background-url: url('spam.jpg');\n}"
        )
        self.assertEqual(
            converter.convert("p {\n  background-url: url('ham.jpg');\n}", ""),
            "p {\n  background-url: url('spam.jpg');\n}"
        )
        self.assertEqual(
            converter.convert(""".external_link:first-child:before {
  content: "Zobacz także:";
  background: url(картинка.png); }
""", ""),
            """.external_link:first-child:before {
  content: "Zobacz także:";
  background: url('spam.jpg'); }
""")


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(URLConverterTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
