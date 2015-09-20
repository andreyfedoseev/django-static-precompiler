# coding: utf-8
import pytest

from static_precompiler import compilers, exceptions


def clean_javascript(js):
    """ Remove comments and all blank lines. """
    return "\n".join(
        line for line in js.split("\n") if line.strip() and not line.startswith("//")
    )


def test_compile_file():
    compiler = compilers.CoffeeScript()

    assert (
        clean_javascript(compiler.compile_file("scripts/test.coffee")) ==
        """(function() {\n  console.log("Hello, World!");\n}).call(this);"""
    )


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
