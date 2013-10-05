# coding: utf-8
from unittest import main, TestCase
from mock import MagicMock
from static_precompiler.utils import URLConverter


class URLConverterTestCase(TestCase):

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


if __name__ == '__main__':
    main()
