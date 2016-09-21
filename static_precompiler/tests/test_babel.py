# coding: utf-8
import json
import os

import pytest

from static_precompiler import compilers, exceptions
from static_precompiler.utils import safe_open

from .test_coffeescript import clean_javascript


def test_compile_file(monkeypatch, tmpdir):
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.Babel()

    assert compiler.compile_file("scripts/test.es6") == "COMPILED/scripts/test.js"

    full_output_path = compiler.get_full_output_path("scripts/test.es6")

    assert os.path.exists(full_output_path)

    with safe_open(full_output_path) as compiled:
        assert compiled.read() == """console.log("Hello, World!");\n"""

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_file("scripts/broken.es6")


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

    sourcemap = json.loads(safe_open(full_output_path + ".map").read())
    assert sourcemap["sourceRoot"] == "../../scripts"
    assert sourcemap["sources"] == ["test.es6"]
    assert sourcemap["file"] == "test.js"


def test_compile_source():
    compiler = compilers.Babel()

    assert (
        clean_javascript(compiler.compile_source('console.log("Hello, World!");')) ==
        """console.log("Hello, World!");"""
    )

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source('console.log "Hello, World!')

    # Test non-ascii
    assert (
        clean_javascript(compiler.compile_source('console.log("Привет, Мир!");')) ==
        """console.log("Привет, Мир!");"""
    )


def test_get_extra_args():

    compiler = compilers.Babel(modules="foo", plugins="bar", presets="baz")

    assert compiler.get_extra_args() == [
        "--modules", "foo",
        "--plugins", "bar",
        "--presets", "baz",
    ]
