# coding: utf-8
from static_precompiler.compilers.es6to5 import ES6To5
from static_precompiler.exceptions import StaticCompilationError
from test_coffeescript import clean_javascript
import pytest


def test_compile_file():
    compiler = ES6To5()

    assert clean_javascript(compiler.compile_file("scripts/test.es6")) == """"use strict";\nconsole.log("Hello, World!");"""


def test_compile_source():
    compiler = ES6To5()

    assert clean_javascript(compiler.compile_source('console.log("Hello, World!");')) == """"use strict";\nconsole.log("Hello, World!");"""

    with pytest.raises(StaticCompilationError):
        compiler.compile_source('console.log "Hello, World!')

    # Test non-ascii
    assert clean_javascript(compiler.compile_source('console.log("Привет, Мир!");')) == """"use strict";\nconsole.log("Привет, Мир!");"""
