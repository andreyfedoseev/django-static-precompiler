# coding: utf-8
from static_precompiler import utils


def test_convert_url():
    converter = utils.URLConverter()

    assert converter.convert_url("http://dummy.jpg", "styles/") == "'http://dummy.jpg'"
    assert converter.convert_url("https://dummy.jpg", "styles/") == "'https://dummy.jpg'"
    assert converter.convert_url("/dummy.jpg", "styles/") == "'/dummy.jpg'"
    assert converter.convert_url("data:abc", "styles/") == "'data:abc'"
    assert converter.convert_url("dummy.jpg", "styles/") == "'/static/styles/dummy.jpg'"
    assert converter.convert_url("./dummy.jpg", "styles/") == "'/static/styles/dummy.jpg'"
    assert converter.convert_url("../images/dummy.jpg", "styles/") == "'/static/images/dummy.jpg'"


def test_convert(monkeypatch):
    converter = utils.URLConverter()

    monkeypatch.setattr(converter, "convert_url", lambda *args: "'spam.jpg'")
    assert (
        converter.convert("p {\n  background-url: url(ham.jpg);\n}", "") ==
        "p {\n  background-url: url('spam.jpg');\n}"
    )
    assert (
        converter.convert(
            'p {\n  background-url: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='
            '\'http://www.w3.org/2000/svg\' viewBox=\'0 0 8 8\'%3E%3Cpath fill='
            '\'rgba(255, 255, 255, 0.97)\' d=\'M6.564.75l-3.59 3.612-1.538-1.55L0 4.26 2.974 7.25 8 '
            '2.193z\'/%3E%3C/svg%3E");\n}', "") ==
        'p {\n  background-url: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='
        '\'http://www.w3.org/2000/svg\' viewBox=\'0 0 8 8\'%3E%3Cpath fill=\'rgba(255, 255, 255, 0.97)'
        '\' d=\'M6.564.75l-3.59 3.612-1.538-1.55L0 4.26 2.974 7.25 8 2.193z\'/%3E%3C/svg%3E");\n}'
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
