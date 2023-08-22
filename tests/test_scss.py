import json
import os
import re

import pytest
from pytest_mock import MockFixture

from static_precompiler import exceptions, utils
from static_precompiler.compilers import dart_sass, libsass


@pytest.fixture(scope="module", params=(libsass, dart_sass))
def compiler_factory(request):
    compiler_module = request.param

    def factory(compiler_type, *args, **kwargs):
        if compiler_module is dart_sass:
            kwargs["executable"] = "/opt/dart-sass/sass"
        if compiler_type == "scss":
            return compiler_module.SCSS(*args, **kwargs)
        elif compiler_type == "sass":
            return compiler_module.SASS(*args, **kwargs)

    return factory


def test_get_full_source_path(compiler_factory):
    compiler = compiler_factory("scss")
    with pytest.raises(ValueError):
        compiler.get_full_source_path("_extra.scss")

    extra_path = os.path.join(os.path.dirname(__file__), "static", "styles", "sass", "extra-path")

    compiler = compiler_factory("scss", load_paths=(extra_path,))

    assert compiler.get_full_source_path("_extra.scss") == os.path.join(extra_path, "_extra.scss")


def test_compile_file(compiler_factory, mocker: MockFixture, tmpdir):
    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)
    convert_urls = mocker.patch("static_precompiler.url_converter.convert_urls", return_value=None)

    compiler = compiler_factory("scss")

    assert compiler.compile_file("styles/sass/test.scss") == "COMPILED/styles/sass/test.css"

    full_output_path = compiler.get_full_output_path("styles/sass/test.scss")
    convert_urls.assert_called_once_with(full_output_path, "styles/sass/test.scss")

    assert os.path.exists(full_output_path)

    with open(full_output_path) as compiled:
        assert utils.normalize_whitespace(compiled.read()) == "p { font-size: 15px; } p a { color: red; }"

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_file("styles/sass/invalid-syntax.scss")


def test_sourcemap(compiler_factory, mocker: MockFixture, tmpdir):
    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)
    mocker.patch("static_precompiler.url_converter.convert_urls", return_value=None)

    compiler = compiler_factory("scss", sourcemap_enabled=False)
    compiler.compile_file("styles/sass/test.scss")
    full_output_path = compiler.get_full_output_path("styles/sass/test.scss")
    assert not os.path.exists(full_output_path + ".map")

    compiler = compiler_factory("scss", sourcemap_enabled=True)
    compiler.compile_file("styles/sass/test.scss")
    full_output_path = compiler.get_full_output_path("styles/sass/test.scss")
    assert os.path.exists(full_output_path + ".map")

    with open(full_output_path + ".map") as sourcemap_file:
        sourcemap = json.load(sourcemap_file)
    assert sourcemap["sourceRoot"] == "../../../styles/sass"
    assert sourcemap["sources"] == ["test.scss"]
    assert sourcemap["file"] == "test.css"

    with open(full_output_path) as compiled_file:
        assert "/*# sourceMappingURL=test.css.map */" in {line.strip() for line in compiled_file.readlines()}


def test_compile_source(compiler_factory):
    compiler = compiler_factory("scss")
    assert (
        utils.normalize_whitespace(compiler.compile_source("p {font-size: 15px; a {color: red;}}"))
        == "p { font-size: 15px; } p a { color: red; }"
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source("invalid syntax")

    # Test non-ascii
    NON_ASCII = """@charset "UTF-8"; .external_link:first-child:before { content: "Zobacz także:"; background: url("картинка.png"); }"""  # noqa
    assert utils.normalize_whitespace(compiler.compile_source(NON_ASCII)) == NON_ASCII

    compiler = compiler_factory("sass")
    assert (
        utils.normalize_whitespace(compiler.compile_source("p\n  font-size: 15px\n  a\n    color: red"))
        == "p { font-size: 15px; } p a { color: red; }"
    )


def test_parse_import_string(compiler_factory):
    compiler = compiler_factory("scss")
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


def test_strip_comments(compiler_factory):
    source = """
// Single-line comment
a {
  color: red;
  font-family: "Foo // Bar";
  background-image: url(/* not a comment */);
  // Another comment
}
/* This
 is *
* a
 multiline
comment */

p {
  /* This is also a comment */
  color: blue;
  background-image: url(//not-a-comment.com); // comment
}
    """
    compiler = compiler_factory("scss")
    assert (
        compiler.strip_comments(source)
        == """
a {
  color: red;
  font-family: "Foo // Bar";
  background-image: url(/* not a comment */);
}

p {
  color: blue;
  background-image: url(//not-a-comment.com);
}
    """
    )


def test_find_imports():
    source = """
@import "foo.css", ;
@import " ";
@import "foo.scss";
@import "foo";
@import "foo.css";
/*
    @import "multi-line-comment";
*/
@import "foo" screen;
@import "http://foo.com/bar";
@import url(foo);  // `.class-name { @import "single-line-comment"; }`).
@import "rounded-corners",
        "text-shadow";
@import url(http://fonts.googleapis.com/css?family=Arvo:400,700,400italic,700italic);
@import url("http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,400,700,600,300");
@import "foo,bar", url(bar,baz), 'bar,foo';
"""

    expected = [
        "bar,foo",
        "foo",
        "foo,bar",
        "foo.scss",
        "rounded-corners",
        "text-shadow",
    ]
    compiler = dart_sass.SCSS()
    assert compiler.find_imports(source) == expected


def test_locate_imported_file(compiler_factory, mocker: MockFixture):
    root = os.path.dirname(__file__)

    existing_files = set()
    for f in ("A/B.scss", "A/_C.scss", "A/S.sass", "D.scss"):
        existing_files.add(os.path.join(root, "static", utils.normalize_path(f)))

    additional_path = os.path.join(root, "static", "additional-path")
    existing_files.add(os.path.join(additional_path, "foo.scss"))

    mocker.patch("os.path.exists", side_effect=lambda x: x in existing_files)

    compiler = compiler_factory("scss", load_paths=(additional_path,))

    assert compiler.locate_imported_file("A", "B.scss") == "A/B.scss"
    assert compiler.locate_imported_file("A", "C") == "A/_C.scss"
    assert compiler.locate_imported_file("E", "../D") == "D.scss"
    assert compiler.locate_imported_file("E", "../A/B.scss") == "A/B.scss"
    assert compiler.locate_imported_file("", "D.scss") == "D.scss"
    assert compiler.locate_imported_file("A", "S.sass") == "A/S.sass"
    assert compiler.locate_imported_file("A", "S") == "A/S.sass"
    assert compiler.locate_imported_file("A", "foo") == "foo.scss"
    assert compiler.locate_imported_file("bar", "foo") == "foo.scss"

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.locate_imported_file("", "Z.scss")


def test_find_dependencies(compiler_factory, mocker: MockFixture):
    compiler = compiler_factory("scss")
    files = {
        "A.scss": "@import 'B/C.scss';",
        "B/C.scss": "@import '../E';",
        "_E.scss": "p {color: red;}",
    }
    mocker.patch.object(compiler, "get_source", side_effect=lambda x: files[x])

    root = os.path.dirname(__file__)

    existing_files = set()
    for f in files:
        existing_files.add(os.path.join(root, "static", utils.normalize_path(f)))

    mocker.patch("os.path.exists", side_effect=lambda x: x in existing_files)

    assert compiler.find_dependencies("A.scss") == ["B/C.scss", "_E.scss"]
    assert compiler.find_dependencies("B/C.scss") == ["_E.scss"]
    assert compiler.find_dependencies("_E.scss") == []


def test_get_extra_args():
    assert dart_sass.SCSS().get_extra_args() == []

    assert dart_sass.SCSS(load_paths=["foo", "bar"], output_style="compact").get_extra_args() == [
        "-I",
        "foo",
        "-I",
        "bar",
        "-s",
        "compact",
    ]


def test_load_paths(compiler_factory, mocker: MockFixture, tmpdir, settings):
    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)
    mocker.patch("static_precompiler.url_converter.convert_urls", return_value=None)

    compiler = compiler_factory("scss")
    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_file("styles/sass/load-paths.scss")

    compiler = compiler_factory("scss", load_paths=[os.path.join(settings.STATIC_ROOT, "styles", "sass", "extra-path")])

    compiler.compile_file("styles/sass/load-paths.scss")

    full_output_path = compiler.get_full_output_path("styles/sass/load-paths.scss")
    assert os.path.exists(full_output_path)

    with open(full_output_path) as compiled:
        assert utils.normalize_whitespace(compiled.read()) == "p { font-weight: bold; }"


@pytest.mark.parametrize("precision", (None, 10))
def test_precision(precision, mocker: MockFixture, tmpdir):
    expected_precision = 5 if precision is None else precision

    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)
    mocker.patch("static_precompiler.url_converter.convert_urls", return_value=None)

    compiler = libsass.SCSS(precision=precision)

    compiler.compile_file("styles/sass/precision.scss")

    full_output_path = compiler.get_full_output_path("styles/sass/precision.scss")
    assert os.path.exists(full_output_path)

    with open(full_output_path) as compiled:
        compiled_css = compiled.read()
        match = re.search(r"line-height: (.+?);", compiled_css)
        assert match
        line_height = match.groups()[0]
        assert len(line_height.split(".")[-1]) == expected_precision


def test_output_style(compiler_factory, mocker: MockFixture, tmpdir):
    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)
    mocker.patch("static_precompiler.url_converter.convert_urls", return_value=None)

    compiler = compiler_factory("scss", output_style="compressed")

    compiler.compile_file("styles/sass/test.scss")

    full_output_path = compiler.get_full_output_path("styles/sass/test.scss")
    assert os.path.exists(full_output_path)

    with open(full_output_path) as compiled:
        assert compiled.read() == "p{font-size:15px}p a{color:red}\n"
