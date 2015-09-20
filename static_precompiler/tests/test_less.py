# coding: utf-8
import os

import pretend
import pytest

from static_precompiler import compilers, exceptions, utils


def test_compile_file():
    compiler = compilers.LESS()

    assert compiler.compile_file("styles/test.less") == """p {
  font-size: 15px;
}
p a {
  color: red;
}
h1 {
  color: blue;
}
"""


def test_compile_source():
    compiler = compilers.LESS()

    assert (
        compiler.compile_source("p {font-size: 15px; a {color: red;}}") ==
        "p {\n  font-size: 15px;\n}\np a {\n  color: red;\n}\n"
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source('invalid syntax')

    # Test non-ascii
    NON_ASCII = """.external_link:first-child:before {
  content: "Zobacz także:";
  background: url(картинка.png);
}
"""
    assert compiler.compile_source(NON_ASCII) == NON_ASCII


def test_postprocesss(monkeypatch):
    compiler = compilers.LESS()

    convert_urls = pretend.call_recorder(lambda *args: "spam")

    monkeypatch.setattr("static_precompiler.utils.convert_urls", convert_urls)

    assert compiler.postprocess("ham", "eggs") == "spam"
    assert convert_urls.calls == [pretend.call("ham", "eggs")]


def test_find_imports():
    compiler = compilers.LESS()
    source = """
@import "foo.css";
@import " ";
@import "foo.less";
@import (reference) "reference.less";
@import (inline) "inline.css";
@import (less) "less.less";
@import (css) "css.css";
@import (once) "once.less";
@import (multiple) "multiple.less";
@import "screen.less" screen;
@import url(url-import);
@import 'single-quotes.less';
@import "no-extension";
"""
    expected = sorted([
        "foo.less",
        "reference.less",
        "inline.css",
        "less.less",
        "once.less",
        "multiple.less",
        "screen.less",
        "single-quotes.less",
        "no-extension",
    ])
    assert compiler.find_imports(source) == expected


def test_locate_imported_file(monkeypatch):
    compiler = compilers.LESS()

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in ("A/B.less", "D.less"):
        existing_files.add(os.path.join(root, "static", utils.normalize_path(f)))

    monkeypatch.setattr("os.path.exists", lambda path: path in existing_files)

    assert compiler.locate_imported_file("A", "B.less") == "A/B.less"
    assert compiler.locate_imported_file("E", "../D") == "D.less"
    assert compiler.locate_imported_file("E", "../A/B.less") == "A/B.less"
    assert compiler.locate_imported_file("", "D.less") == "D.less"

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.locate_imported_file("", "Z.less")


def test_find_dependencies(monkeypatch):
    compiler = compilers.LESS()
    files = {
        "A.less": "@import 'B/C.less';",
        "B/C.less": "@import '../E';",
        "E.less": "p {color: red;}",
    }
    monkeypatch.setattr(compiler, "get_source", lambda x: files[x])

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in files:
        existing_files.add(os.path.join(root, "static", utils.normalize_path(f)))

    monkeypatch.setattr("os.path.exists", lambda path: path in existing_files)

    assert compiler.find_dependencies("A.less") == ["B/C.less", "E.less"]
    assert compiler.find_dependencies("B/C.less") == ["E.less"]
    assert compiler.find_dependencies("E.less") == []
