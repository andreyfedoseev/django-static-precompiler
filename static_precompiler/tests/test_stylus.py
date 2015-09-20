# coding: utf-8
import os

import pretend
import pytest

from static_precompiler import compilers, exceptions, utils


def test_compile_file():
    compiler = compilers.Stylus()

    assert utils.fix_line_breaks(compiler.compile_file("styles/stylus/A.styl")) == "p {\n  color: #f00;\n}\n"

    with pytest.raises(exceptions.StaticCompilationError):
        assert compiler.compile_file("styles/stylus/broken1.styl")


def test_compile_source():
    compiler = compilers.Stylus()

    assert utils.fix_line_breaks(compiler.compile_source("p\n  color: red;")) == "p {\n  color: #f00;\n}\n\n"

    with pytest.raises(exceptions.StaticCompilationError):
        assert compiler.compile_source("broken")


def test_postprocesss(monkeypatch):
    compiler = compilers.Stylus()
    convert_urls = pretend.call_recorder(lambda *args: "spam")
    monkeypatch.setattr("static_precompiler.utils.convert_urls", convert_urls)
    assert compiler.postprocess("ham", "eggs") == "spam"
    assert convert_urls.calls == [pretend.call("ham", "eggs")]


def test_find_imports():
    source = """
@import " "
@import "foo.styl"
@import 'foo'
@import "foo.css"
@import "http://foo.com/bar"
@import "https://foo.com/bar"
@import url(foo)
@import url(http://fonts.googleapis.com/css?family=Arvo:400,700,400italic,700italic)
@import url("http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,400,700,600,300")
@require "foo.styl"
@require "foo/*"
"""

    expected = [
        "foo",
        "foo.styl",
        "foo/*",
    ]

    compiler = compilers.Stylus()
    assert compiler.find_imports(source) == expected


def test_locate_imported_file(monkeypatch):
    compiler = compilers.Stylus()

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in ("A/B.styl", "C.styl"):
        existing_files.add(os.path.join(root, "static", utils.normalize_path(f)))

    monkeypatch.setattr("os.path.exists", lambda x: x in existing_files)

    assert compiler.locate_imported_file("A", "B.styl") == "A/B.styl"
    assert compiler.locate_imported_file("", "C.styl") == "C.styl"

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.locate_imported_file("", "Z.styl")


def test_find_dependencies():

    compiler = compilers.Stylus()

    assert compiler.find_dependencies("styles/stylus/A.styl") == [
        "styles/stylus/B/C.styl",
        "styles/stylus/D.styl",
        "styles/stylus/E/F.styl",
        "styles/stylus/E/index.styl",
    ]

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.find_dependencies("styles/stylus/broken1.styl")

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.find_dependencies("styles/stylus/broken2.styl")

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.find_dependencies("styles/stylus/broken3.styl")
