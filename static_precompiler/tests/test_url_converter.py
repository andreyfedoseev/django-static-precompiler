# coding: utf-8
from static_precompiler import utils


def test_convert_url():
    converter = utils.URLConverter()

    assert converter.convert_url("http://dummy.jpg", "styles/") == "http://dummy.jpg"
    assert converter.convert_url("https://dummy.jpg", "styles/") == "https://dummy.jpg"
    assert converter.convert_url("/dummy.jpg", "styles/") == "/dummy.jpg"
    assert converter.convert_url("data:abc", "styles/") == "data:abc"
    assert converter.convert_url("dummy.jpg", "styles/") == "/static/styles/dummy.jpg"
    assert converter.convert_url("./dummy.jpg", "styles/") == "/static/styles/dummy.jpg"
    assert converter.convert_url("../images/dummy.jpg", "styles/") == "/static/images/dummy.jpg"


def test_convert(monkeypatch):
    converter = utils.URLConverter()

    monkeypatch.setattr(converter, "convert_url", lambda *args: "spam.jpg")
    assert (
        converter.convert("p {\n  background-url: url(ham.jpg);\n}", "") ==
        "p {\n  background-url: url('spam.jpg');\n}"
    )
    assert (
        converter.convert('p {\n  background-url: url("ham.jpg");\n}', "") ==
        "p {\n  background-url: url('spam.jpg');\n}"
    )
    assert (
        converter.convert("p {\n  background-url: url('ham.jpg');\n}", "") ==
        "p {\n  background-url: url('spam.jpg');\n}"
    )
    assert converter.convert(""".external_link:first-child:before {
  content: "Zobacz także:";
  background: url(картинка.png); }
""", "") == """.external_link:first-child:before {
  content: "Zobacz także:";
  background: url('spam.jpg'); }
"""
