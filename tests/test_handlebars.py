import json
import os
from pathlib import Path

import pytest

from static_precompiler import compilers, exceptions


def clean_javascript(js):
    """Remove comments and all blank lines."""
    return "\n".join(line for line in js.split("\n") if line.strip() and not line.startswith("//"))


def test_is_supported():
    compiler = compilers.Handlebars()

    assert compiler.is_supported("test.hbs")
    assert compiler.is_supported("test.handlebars")
    assert not compiler.is_supported("test.foo")


def test_compile_file(monkeypatch, tmpdir):
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.Handlebars()

    assert clean_javascript(compiler.compile_file("scripts/test.hbs")) == "COMPILED/scripts/test.js"
    full_output_path = Path(compiler.get_full_output_path("scripts/test.hbs"))
    assert full_output_path.exists()

    compiled = clean_javascript(full_output_path.read_text())
    assert (
        compiled
        == """(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['test'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };
  return "<h1>"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":1,"column":4},"end":{"line":1,"column":13}}}) : helper)))
    + "</h1>\\n";
},"useData":true});
})();"""  # noqa: E501
    )

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

    compiled = clean_javascript(compiler.compile_source("<h1>{{title}}</h1>"))
    assert (
        compiled
        == """{"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };
  return "<h1>"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":1,"column":4},"end":{"line":1,"column":13}}}) : helper)))
    + "</h1>";
},"useData":true}"""  # noqa
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source("{{title}")

    # Test non-ascii
    compiled = clean_javascript(compiler.compile_source("<h1>Заголовок {{title}}</h1>"))
    assert (
        compiled
        == """{"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };
  return "<h1>Заголовок "
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":1,"column":14},"end":{"line":1,"column":23}}}) : helper)))
    + "</h1>";
},"useData":true}"""  # noqa
    )


def test_find_dependencies():
    return []


def test_get_extra_args(monkeypatch):
    compiler = compilers.Handlebars(known_helpers=["foo", "bar"], namespace="baz", simple=True)

    assert compiler.get_extra_args() == ["-k", "foo", "-k", "bar", "-n", "baz", "-s"]
