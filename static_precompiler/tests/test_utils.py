import django.core.exceptions
import pytest
from pretend import stub

from static_precompiler import compilers, exceptions, utils


def test_build_compilers(monkeypatch):

    monkeypatch.setattr("static_precompiler.settings.COMPILERS", ["invalid_classpath"])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        utils.build_compilers()

    monkeypatch.setattr("static_precompiler.settings.COMPILERS", ["non_existing_module.ClassName"])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        utils.build_compilers()

    monkeypatch.setattr("static_precompiler.settings.COMPILERS", ["static_precompiler.NonExistingClass"])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        utils.build_compilers()

    monkeypatch.setattr("static_precompiler.settings.COMPILERS", ["static_precompiler.compilers.CoffeeScript"])
    built_compilers = utils.build_compilers()
    assert list(built_compilers.keys()) == ["coffeescript"]
    assert isinstance(built_compilers["coffeescript"], compilers.CoffeeScript)

    monkeypatch.setattr("static_precompiler.settings.COMPILERS", [("static_precompiler.compilers.CoffeeScript", )])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        utils.build_compilers()

    monkeypatch.setattr("static_precompiler.settings.COMPILERS", [("static_precompiler.compilers.CoffeeScript", "foo")])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        utils.build_compilers()

    monkeypatch.setattr("static_precompiler.settings.COMPILERS",
                        [("static_precompiler.compilers.CoffeeScript", "foo", "bar")])
    with pytest.raises(django.core.exceptions.ImproperlyConfigured):
        utils.build_compilers()

    monkeypatch.setattr("static_precompiler.settings.COMPILERS",
                        [("static_precompiler.compilers.CoffeeScript", {"executable": "foo"})])
    built_compilers = utils.build_compilers()
    assert list(built_compilers.keys()) == ["coffeescript"]
    assert isinstance(built_compilers["coffeescript"], compilers.CoffeeScript)
    assert built_compilers["coffeescript"].executable == "foo"


def test_get_compiler_by_name(monkeypatch):

    compiler_stub = stub()

    monkeypatch.setattr("static_precompiler.utils.get_compilers", lambda: {
        "foo": compiler_stub,
    })

    with pytest.raises(exceptions.CompilerNotFound):
        utils.get_compiler_by_name("bar")

    assert utils.get_compiler_by_name("foo") is compiler_stub


def test_get_compiler_by_path(monkeypatch):

    coffeescript_compiler_stub = stub(is_supported=lambda source_path: source_path.endswith(".coffee"))
    less_compiler_stub = stub(is_supported=lambda source_path: source_path.endswith(".less"))

    monkeypatch.setattr("static_precompiler.utils.get_compilers", lambda: {
        "coffeescript": coffeescript_compiler_stub,
        "less": less_compiler_stub,
    })

    with pytest.raises(exceptions.UnsupportedFile):
        utils.get_compiler_by_path("test.sass")

    assert utils.get_compiler_by_path("test.coffee") is coffeescript_compiler_stub
    assert utils.get_compiler_by_path("test.less") is less_compiler_stub


def test_compile_static(monkeypatch):

    compiler_stub = stub(
        compile=lambda x: "compiled",
        compile_lazy=lambda x: "compiled lazy"
    )

    monkeypatch.setattr("static_precompiler.utils.get_compiler_by_path", lambda path: compiler_stub)

    assert utils.compile_static("foo") == "compiled"
    assert utils.compile_static_lazy("foo") == "compiled lazy"
