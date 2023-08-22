import django.core.exceptions
import pytest
from pytest_mock import MockFixture

from static_precompiler import compilers, exceptions, registry


def test_build_compilers(mocker: MockFixture):
    mocker.patch("static_precompiler.settings.COMPILERS", ["invalid_classpath"])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        registry.build_compilers()

    mocker.patch("static_precompiler.settings.COMPILERS", ["non_existing_module.ClassName"])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        registry.build_compilers()

    mocker.patch("static_precompiler.settings.COMPILERS", ["static_precompiler.NonExistingClass"])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        registry.build_compilers()

    mocker.patch("static_precompiler.settings.COMPILERS", ["static_precompiler.compilers.CoffeeScript"])
    built_compilers = registry.build_compilers()
    assert list(built_compilers.keys()) == ["coffeescript"]
    assert isinstance(built_compilers["coffeescript"], compilers.CoffeeScript)

    mocker.patch("static_precompiler.settings.COMPILERS", [("static_precompiler.compilers.CoffeeScript",)])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        registry.build_compilers()

    mocker.patch("static_precompiler.settings.COMPILERS", [("static_precompiler.compilers.CoffeeScript", "foo")])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        registry.build_compilers()

    mocker.patch("static_precompiler.settings.COMPILERS", [("static_precompiler.compilers.CoffeeScript", "foo", "bar")])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        registry.build_compilers()

    mocker.patch(
        "static_precompiler.settings.COMPILERS", [("static_precompiler.compilers.CoffeeScript", {"executable": "foo"})]
    )
    built_compilers = registry.build_compilers()
    assert list(built_compilers.keys()) == ["coffeescript"]
    coffeescript = built_compilers["coffeescript"]
    assert isinstance(coffeescript, compilers.CoffeeScript)
    assert coffeescript.executable == "foo"


def test_get_compiler_by_name(mocker: MockFixture):
    compiler = mocker.MagicMock(spec=compilers.BaseCompiler)

    mocker.patch("static_precompiler.registry.get_compilers", return_value={"foo": compiler})

    with pytest.raises(exceptions.CompilerNotFound):
        registry.get_compiler_by_name("bar")

    assert registry.get_compiler_by_name("foo") is compiler


def test_get_compiler_by_path(mocker: MockFixture):
    coffeescript_compiler = mocker.MagicMock(spec=compilers.BaseCompiler)
    coffeescript_compiler.is_supported.side_effect = lambda source_path: source_path.endswith(".coffee")
    less_compiler = mocker.MagicMock(spec=compilers.BaseCompiler)
    less_compiler.is_supported.side_effect = lambda source_path: source_path.endswith(".less")

    mocker.patch(
        "static_precompiler.registry.get_compilers",
        return_value={
            "coffeescript": coffeescript_compiler,
            "less": less_compiler,
        },
    )

    with pytest.raises(exceptions.UnsupportedFile):
        registry.get_compiler_by_path("test.sass")

    assert registry.get_compiler_by_path("test.coffee") is coffeescript_compiler
    assert registry.get_compiler_by_path("test.less") is less_compiler
