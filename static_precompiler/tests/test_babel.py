# coding: utf-8
import os

import pytest

from static_precompiler import compilers, exceptions

from .test_coffeescript import clean_javascript


def test_compile_file(monkeypatch, tmpdir):
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.Babel()

    assert compiler.compile_file("scripts/test.es6") == "COMPILED/scripts/test.js"

    full_output_path = compiler.get_full_output_path("scripts/test.es6")

    assert os.path.exists(full_output_path)

    with open(full_output_path) as compiled:
        assert compiled.read() == """"use strict";

console.log("Hello, World!");
"""


def test_sourcemap(monkeypatch, tmpdir):

    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.Babel(sourcemap_enabled=False)
    compiler.compile_file("scripts/test.es6")
    full_output_path = compiler.get_full_output_path("scripts/test.es6")
    assert not os.path.exists(full_output_path + ".map")

    compiler = compilers.Babel(sourcemap_enabled=True)
    compiler.compile_file("scripts/test.es6")
    full_output_path = compiler.get_full_output_path("scripts/test.es6")
    assert os.path.exists(full_output_path + ".map")


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
