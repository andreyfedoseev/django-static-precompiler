# coding: utf-8
import pytest

from static_precompiler import compilers, exceptions

from .test_coffeescript import clean_javascript


def test_compile_file():
    compiler = compilers.Babel()

    assert (
        clean_javascript(compiler.compile_file("scripts/test.es6")) ==
        """"use strict";\nconsole.log("Hello, World!");"""
    )


def test_compile_source():
    compiler = compilers.Babel()

    assert (
        clean_javascript(compiler.compile_source('console.log("Hello, World!");')) ==
        """"use strict";\nconsole.log("Hello, World!");"""
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source('console.log "Hello, World!')

    # Test non-ascii
    assert (
        clean_javascript(compiler.compile_source('console.log("Привет, Мир!");')) ==
        """"use strict";\nconsole.log("Привет, Мир!");"""
    )
