import json
import os
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from static_precompiler import compilers, exceptions

from .test_coffeescript import clean_javascript


def test_compile_file(mocker: MockFixture, tmpdir):
    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.TypeScript()

    assert compiler.compile_file("scripts/test.ts") == "COMPILED/scripts/test.js"

    full_output_path = compiler.get_full_output_path("scripts/test.ts")

    assert os.path.exists(full_output_path)

    with open(full_output_path) as compiled:
        content = clean_javascript(compiled.read())
        assert 'var greeting = "Hello, World!";' in content or 'const greeting = "Hello, World!";' in content
        assert "console.log(greeting);" in content


def test_sourcemap(mocker: MockFixture, tmpdir):
    mocker.patch("static_precompiler.settings.ROOT", tmpdir.strpath)

    compiler = compilers.TypeScript(sourcemap_enabled=False)
    compiler.compile_file("scripts/test.ts")
    full_output_path = compiler.get_full_output_path("scripts/test.ts")
    assert not os.path.exists(full_output_path + ".map")

    compiler = compilers.TypeScript(sourcemap_enabled=True)
    compiler.compile_file("scripts/test.ts")
    full_output_path = compiler.get_full_output_path("scripts/test.ts")
    assert os.path.exists(full_output_path + ".map")

    with open(full_output_path + ".map") as sourcemap_file:
        sourcemap = json.load(sourcemap_file)
    assert sourcemap["sources"] == ["test.ts"]
    assert sourcemap["file"] == "test.js"


def test_compile_source():
    compiler = compilers.TypeScript()

    compiled = clean_javascript(compiler.compile_source('const greeting: string = "Hello, World!"; console.log(greeting);'))
    assert 'var greeting = "Hello, World!";' in compiled or 'const greeting = "Hello, World!";' in compiled
    assert "console.log(greeting);" in compiled

    with pytest.raises(exceptions.StaticCompilationError):
        compiler.compile_source('const invalid: number = "not a number;')

    # Test non-ascii
    compiled_unicode = clean_javascript(compiler.compile_source('const msg: string = "Привет, Мир!"; console.log(msg);'))
    assert "Привет, Мир!" in compiled_unicode


def test_get_extra_args():
    compiler = compilers.TypeScript(target="ES2020", module="commonjs")
    assert compiler.get_extra_args() == [
        "--target",
        "ES2020",
        "--module",
        "commonjs",
    ]
