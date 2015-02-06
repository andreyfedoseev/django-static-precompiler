from django.core.exceptions import ImproperlyConfigured
from static_precompiler.exceptions import UnsupportedFile, CompilerNotFound
# noinspection PyProtectedMember
from static_precompiler.utils import _build_compilers, get_compilers, get_compiler_by_name, get_compiler_by_path, compile_static,\
    compile_static_lazy
from static_precompiler.compilers import CoffeeScript
from pretend import stub
import pytest


def test_build_compilers(monkeypatch):

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", ["invalid_classpath"])
    with pytest.raises(ImproperlyConfigured):
        _build_compilers()

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", ["non_existing_module.ClassName"])
    with pytest.raises(ImproperlyConfigured):
        _build_compilers()

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", ["static_precompiler.NonExistingClass"])
    with pytest.raises(ImproperlyConfigured):
        _build_compilers()

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", ["static_precompiler.compilers.CoffeeScript"])
    compilers = _build_compilers()
    assert list(compilers.keys()) == ["coffeescript"]
    assert isinstance(compilers["coffeescript"], CoffeeScript)

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", [("static_precompiler.compilers.CoffeeScript", )])
    with pytest.raises(ImproperlyConfigured):
        _build_compilers()

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", [("static_precompiler.compilers.CoffeeScript", "foo")])
    with pytest.raises(ImproperlyConfigured):
        _build_compilers()

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", [("static_precompiler.compilers.CoffeeScript", "foo", "bar")])
    with pytest.raises(ImproperlyConfigured):
        _build_compilers()

    monkeypatch.setattr("static_precompiler.utils.COMPILERS", [("static_precompiler.compilers.CoffeeScript", {"executable": "foo"})])
    compilers = _build_compilers()
    assert list(compilers.keys()) == ["coffeescript"]
    assert isinstance(compilers["coffeescript"], CoffeeScript)
    assert compilers["coffeescript"].executable == "foo"


def test_get_compiler_by_name(monkeypatch):

    compiler_stub = stub()

    monkeypatch.setattr("static_precompiler.utils.get_compilers", lambda: {
        "foo": compiler_stub,
    })

    with pytest.raises(CompilerNotFound):
        get_compiler_by_name("bar")

    assert get_compiler_by_name("foo") is compiler_stub


def test_get_compiler_by_path(monkeypatch):

    coffeescript_compiler_stub = stub(is_supported=lambda source_path: source_path.endswith(".coffee"))
    less_compiler_stub = stub(is_supported=lambda source_path: source_path.endswith(".less"))

    monkeypatch.setattr("static_precompiler.utils.get_compilers", lambda: {
        "coffeescript": coffeescript_compiler_stub,
        "less": less_compiler_stub,
    })

    with pytest.raises(UnsupportedFile):
        get_compiler_by_path("test.sass")

    assert get_compiler_by_path("test.coffee") is coffeescript_compiler_stub
    assert get_compiler_by_path("test.less") is less_compiler_stub


def test_compile_static(monkeypatch):

    compiler_stub = stub(
        compile=lambda x: "compiled",
        compile_lazy=lambda x: "compiled lazy"
    )

    monkeypatch.setattr("static_precompiler.utils.get_compiler_by_path", lambda path: compiler_stub)

    assert compile_static("foo") == "compiled"
    assert compile_static_lazy("foo") == "compiled lazy"
