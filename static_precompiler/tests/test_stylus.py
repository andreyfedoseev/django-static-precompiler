# coding: utf-8
import os

import pytest
from pretend import call, call_recorder

from static_precompiler.compilers import Stylus
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.utils import fix_line_breaks, normalize_path


def test_compile_file():
    compiler = Stylus()

    assert fix_line_breaks(compiler.compile_file("styles/stylus/A.styl")) == "p {\n  color: #f00;\n}\n"

    with pytest.raises(StaticCompilationError):
        assert compiler.compile_file("styles/stylus/broken1.styl")


def test_compile_source():
    compiler = Stylus()

    assert fix_line_breaks(compiler.compile_source("p\n  color: red;")) == "p {\n  color: #f00;\n}\n\n"

    with pytest.raises(StaticCompilationError):
        assert compiler.compile_source("broken")


def test_postprocesss(monkeypatch):
    compiler = Stylus()
    convert_urls = call_recorder(lambda *args: "spam")
    monkeypatch.setattr("static_precompiler.compilers.stylus.convert_urls", convert_urls)
    assert compiler.postprocess("ham", "eggs") == "spam"
    assert convert_urls.calls == [call("ham", "eggs")]


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

    compiler = Stylus()
    assert compiler.find_imports(source) == expected


def test_locate_imported_file(monkeypatch):
    compiler = Stylus()

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in ("A/B.styl", "C.styl"):
        existing_files.add(os.path.join(root, "static", normalize_path(f)))

    monkeypatch.setattr("os.path.exists", lambda x: x in existing_files)

    assert compiler.locate_imported_file("A", "B.styl") == "A/B.styl"
    assert compiler.locate_imported_file("", "C.styl") == "C.styl"

    with pytest.raises(StaticCompilationError):
        compiler.locate_imported_file("", "Z.styl")


def test_find_dependencies():

    compiler = Stylus()

    assert compiler.find_dependencies("styles/stylus/A.styl") == [
        "styles/stylus/B/C.styl",
        "styles/stylus/D.styl",
        "styles/stylus/E/F.styl",
        "styles/stylus/E/index.styl",
    ]

    with pytest.raises(StaticCompilationError):
        compiler.find_dependencies("styles/stylus/broken1.styl")

    with pytest.raises(StaticCompilationError):
        compiler.find_dependencies("styles/stylus/broken2.styl")

    with pytest.raises(StaticCompilationError):
        compiler.find_dependencies("styles/stylus/broken3.styl")
