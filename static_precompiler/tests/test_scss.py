# coding: utf-8
from pretend import call_recorder, call
from static_precompiler.compilers import SCSS, SASS
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.utils import normalize_path, fix_line_breaks
import os
import pytest


def test_compile_file():
    compiler = SCSS()

    assert fix_line_breaks(compiler.compile_file("styles/test.scss")) == "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"


def test_compile_source():
    compiler = SCSS(executable="scss")
    assert fix_line_breaks(compiler.compile_source("p {font-size: 15px; a {color: red;}}")) == "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"

    compiler = SCSS(executable="sass")
    assert fix_line_breaks(compiler.compile_source("p {font-size: 15px; a {color: red;}}")) == "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"

    with pytest.raises(StaticCompilationError):
        compiler.compile_source('invalid syntax')

    with pytest.raises(StaticCompilationError):
        compiler.compile_source('invalid syntax')

    # Test non-ascii
    NON_ASCII = """@charset "UTF-8";
.external_link:first-child:before {
  content: "Zobacz także:";
  background: url(картинка.png); }
"""
    assert fix_line_breaks(compiler.compile_source(NON_ASCII)) == NON_ASCII

    compiler = SASS(executable="sass")
    assert fix_line_breaks(compiler.compile_source("p\n  font-size: 15px\n  a\n    color: red")) == "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"
    compiler = SASS(executable="scss")
    assert fix_line_breaks(compiler.compile_source("p\n  font-size: 15px\n  a\n    color: red")) == "p {\n  font-size: 15px; }\n  p a {\n    color: red; }\n"


def test_postprocesss(monkeypatch):
    compiler = SCSS()
    convert_urls = call_recorder(lambda *args: "spam")
    monkeypatch.setattr("static_precompiler.compilers.scss.convert_urls", convert_urls)
    assert compiler.postprocess("ham", "eggs") == "spam"
    assert convert_urls.calls == [call("ham", "eggs")]


def test_parse_import_string():
    compiler = SCSS()
    import_string = """"foo, bar" , "foo", url(bar,baz),
     'bar,foo',bar screen, projection"""
    assert compiler.parse_import_string(import_string) == [
        "bar",
        "bar,foo",
        "foo",
        "foo, bar",
    ]

    import_string = """"foo,bar", url(bar,baz), 'bar,foo',bar screen, projection"""
    assert compiler.parse_import_string(import_string) == [
        "bar",
        "bar,foo",
        "foo,bar",
    ]

    import_string = """"foo" screen"""
    assert compiler.parse_import_string(import_string) == ["foo"]


def test_find_imports():
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
    compiler = SCSS(compass_enabled=False)
    assert compiler.find_imports(source) == expected

    compiler = SCSS(compass_enabled=True)
    expected = [
        "bar,foo",
        "foo",
        "foo,bar",
        "foo.scss",
        "rounded-corners",
        "text-shadow",
    ]
    assert compiler.find_imports(source) == expected


def test_locate_imported_file(monkeypatch):
    compiler = SCSS()

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in ("A/B.scss", "A/_C.scss", "A/S.sass", "D.scss"):
        existing_files.add(os.path.join(root, "static", normalize_path(f)))

    monkeypatch.setattr("os.path.exists", lambda x: x in existing_files)

    assert compiler.locate_imported_file("A", "B.scss") == "A/B.scss"
    assert compiler.locate_imported_file("A", "C") == "A/_C.scss"
    assert compiler.locate_imported_file("E", "../D") == "D.scss"
    assert compiler.locate_imported_file("E", "../A/B.scss") == "A/B.scss"
    assert compiler.locate_imported_file("", "D.scss") == "D.scss"
    assert compiler.locate_imported_file("A", "S.sass") == "A/S.sass"
    assert compiler.locate_imported_file("A", "S") == "A/S.sass"

    with pytest.raises(StaticCompilationError):
        compiler.locate_imported_file("", "Z.scss")


def test_find_dependencies(monkeypatch):
    compiler = SCSS()
    files = {
        "A.scss": "@import 'B/C.scss';",
        "B/C.scss": "@import '../E';",
        "_E.scss": "p {color: red;}",
        "compass-import.scss": '@import "compass"',
    }
    monkeypatch.setattr("static_precompiler.compilers.scss.SCSS.get_source", lambda self, x: files[x])

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in files:
        existing_files.add(os.path.join(root, "static", normalize_path(f)))

    monkeypatch.setattr("os.path.exists", lambda x: x in existing_files)

    assert compiler.find_dependencies("A.scss") == ["B/C.scss", "_E.scss"]
    assert compiler.find_dependencies("B/C.scss") == ["_E.scss"]
    assert compiler.find_dependencies("_E.scss") == []


def test_compass():
    compiler = SCSS(compass_enabled=True)

    assert fix_line_breaks(compiler.compile_file("test-compass.scss")) == "p {\n  background: url('/static/images/test.png'); }\n"


def test_compass_import():
    compiler = SCSS(compass_enabled=True)

    assert fix_line_breaks(compiler.compile_file("styles/test-compass-import.scss")) == ".round-corners {\n  -moz-border-radius: 4px / 4px;\n  -webkit-border-radius: 4px 4px;\n  border-radius: 4px / 4px; }\n"

    compiler = SCSS(compass_enabled=False)
    with pytest.raises(StaticCompilationError):
        compiler.compile_file("styles/test-compass-import.scss")
