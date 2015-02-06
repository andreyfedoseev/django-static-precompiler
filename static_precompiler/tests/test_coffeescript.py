# coding: utf-8
from static_precompiler.compilers.coffeescript import CoffeeScript
from static_precompiler.exceptions import StaticCompilationError
import pytest


def clean_javascript(js):
    """ Remove comments and all blank lines. """
    return "\n".join(
        line for line in js.split("\n") if line.strip() and not line.startswith("//")
    )


def test_compile_file():
    compiler = CoffeeScript()

    assert clean_javascript(compiler.compile_file("scripts/test.coffee")) == """(function() {\n  console.log("Hello, World!");\n}).call(this);"""


def test_compile_source():
    compiler = CoffeeScript()

    assert clean_javascript(compiler.compile_source('console.log "Hello, World!"')) == """(function() {\n  console.log("Hello, World!");\n}).call(this);"""

    with pytest.raises(StaticCompilationError):
        compiler.compile_source('console.log "Hello, World!')

    # Test non-ascii
    assert clean_javascript(compiler.compile_source('console.log "Привет, Мир!"')) == """(function() {\n  console.log("Привет, Мир!");\n}).call(this);"""
