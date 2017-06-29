# coding: utf-8
import json
import os

import pytest

from static_precompiler import compilers, exceptions


def clean_javascript(js):
    """ Remove comments and all blank lines. """
    return "\n".join(
        line for line in js.split("\n") if line.strip() and not line.startswith("//")
    )


def test_is_supported():

    compiler = compilers.Handlebars()

    assert compiler.is_supported("test.hbs")
    assert compiler.is_supported("test.handlebars")
    assert not compiler.is_supported("test.foo")


def test_compile_file(monkeypatch, tmpdir):
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.Handlebars()

    assert clean_javascript(compiler.compile_file("scripts/test.hbs")) == "COMPILED/scripts/test.js"
    full_output_path = compiler.get_full_output_path("scripts/test.hbs")
    assert os.path.exists(full_output_path)
    with open(full_output_path) as compiled:
        assert clean_javascript(compiled.read()) == """(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['test'] = template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper;
  return "<h1>"
    + container.escapeExpression(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0,{"name":"title","hash":{},"data":data}) : helper)))
    + "</h1>\\n";
},"useData":true});
})();"""  # noqa

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_file("scripts/broken.handlebars")


def test_sourcemap(monkeypatch, tmpdir):

    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.Handlebars(sourcemap_enabled=False)
    compiler.compile_file("scripts/test.hbs")
    full_output_path = compiler.get_full_output_path("scripts/test.hbs")
    assert not os.path.exists(full_output_path + ".map")

    compiler = compilers.Handlebars(sourcemap_enabled=True)
    compiler.compile_file("scripts/test.hbs")
    full_output_path = compiler.get_full_output_path("scripts/test.hbs")
    assert os.path.exists(full_output_path + ".map")

    with open(full_output_path + ".map") as sourcemap_file:
        sourcemap = json.load(sourcemap_file)
    assert sourcemap["sourceRoot"] == "../../scripts"
    assert sourcemap["sources"] == ["test.hbs"]
    assert sourcemap["file"] == "test.js"


def test_compile_source():
    compiler = compilers.Handlebars()

    assert (
        clean_javascript(compiler.compile_source('<h1>{{title}}</h1>')) ==
        """{"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper;
  return "<h1>"
    + container.escapeExpression(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0,{"name":"title","hash":{},"data":data}) : helper)))
    + "</h1>";
},"useData":true}"""  # noqa
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source('{{title}')

    # Test non-ascii
    assert (
        clean_javascript(compiler.compile_source('<h1>Заголовок {{title}}</h1>')) ==
        """{"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper;
  return "<h1>Заголовок "
    + container.escapeExpression(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0,{"name":"title","hash":{},"data":data}) : helper)))
    + "</h1>";
},"useData":true}"""  # noqa
    )


def test_find_dependencies():
    return []


def test_get_extra_args(monkeypatch):

    compiler = compilers.Handlebars(known_helpers=["foo", "bar"], namespace="baz", simple=True)

    assert compiler.get_extra_args() == [
        "-k", "foo",
        "-k", "bar",
        "-n", "baz",
        "-s"
    ]

    with pytest.raises(ValueError):
        compilers.Handlebars(known_helpers="foo")
