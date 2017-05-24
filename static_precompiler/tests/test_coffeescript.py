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


def test_compile_file(monkeypatch, tmpdir):
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.CoffeeScript()

    assert clean_javascript(compiler.compile_file("scripts/test.coffee")) == "COMPILED/scripts/test.js"
    assert os.path.exists(compiler.get_full_output_path("scripts/test.coffee"))
    with open(compiler.get_full_output_path("scripts/test.coffee")) as compiled:
        assert clean_javascript(compiled.read()) == """(function() {\n  console.log("Hello, World!");\n}).call(this);"""


def test_sourcemap(monkeypatch, tmpdir):

    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.CoffeeScript(sourcemap_enabled=False)
    compiler.compile_file("scripts/test.coffee")
    full_output_path = compiler.get_full_output_path("scripts/test.coffee")
    assert not os.path.exists(os.path.splitext(full_output_path)[0] + ".map")

    compiler = compilers.CoffeeScript(sourcemap_enabled=True)
    compiler.compile_file("scripts/test.coffee")
    full_output_path = compiler.get_full_output_path("scripts/test.coffee")
    assert os.path.exists(os.path.splitext(full_output_path)[0] + ".map")

    with open(os.path.splitext(full_output_path)[0] + ".map") as sourcemap_file:
        sourcemap = json.load(sourcemap_file)
    assert sourcemap["sourceRoot"] == "../../scripts"
    assert sourcemap["sources"] == ["test.coffee"]
    assert sourcemap["file"] == "test.js"


def test_compile_source():
    compiler = compilers.CoffeeScript()

    assert (
        clean_javascript(compiler.compile_source('console.log "Hello, World!"')) ==
        """(function() {\n  console.log("Hello, World!");\n}).call(this);"""
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source('console.log "Hello, World!')

    # Test non-ascii
    assert (
        clean_javascript(compiler.compile_source('console.log "Привет, Мир!"')) ==
        """(function() {\n  console.log("Привет, Мир!");\n}).call(this);"""
    )
