import os

import pretend
import pytest
from django.utils import encoding

from static_precompiler import compilers, models, settings


def test_is_supported(monkeypatch):

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.input_extension", "foo")
    compiler = compilers.BaseCompiler()

    assert compiler.is_supported("test.foo") is True
    assert compiler.is_supported("test.bar") is False
    assert compiler.is_supported("foo.test") is False


def test_get_output_filename(monkeypatch):

    compiler = compilers.BaseCompiler()

    monkeypatch.setattr(compiler, "input_extension", "coffee")
    monkeypatch.setattr(compiler, "output_extension", "js")

    assert compiler.get_output_filename("dummy.coffee") == "dummy.js"
    assert compiler.get_output_filename("dummy.coffee.coffee") == "dummy.coffee.js"


def test_get_full_source_path():
    compiler = compilers.BaseCompiler()

    root = os.path.dirname(__file__)

    assert (
        compiler.get_full_source_path("scripts/test.coffee") ==
        os.path.join(root, "static", "scripts", "test.coffee")
    )

    with pytest.raises(ValueError):
        compiler.get_full_source_path("scripts/does-not-exist.coffee")

    assert (
        compiler.get_full_source_path("another_test.coffee") ==
        os.path.normpath(os.path.join(root, "staticfiles_dir", "another_test.coffee"))
    )

    assert (
        compiler.get_full_source_path("prefix/another_test.coffee") ==
        os.path.normpath(os.path.join(root, "staticfiles_dir_with_prefix", "another_test.coffee"))
    )


def test_get_output_path(monkeypatch):

    compiler = compilers.BaseCompiler()
    monkeypatch.setattr(compiler, "get_output_filename", lambda source_path: source_path.replace(".coffee", ".js"))

    assert compiler.get_output_path("scripts/test.coffee") == settings.OUTPUT_DIR + "/scripts/test.js"
    assert compiler.get_output_path("/scripts/test.coffee") == settings.OUTPUT_DIR + "/scripts/test.js"


def test_get_full_output_path(monkeypatch):

    compiler = compilers.BaseCompiler()
    monkeypatch.setattr(compiler, "get_output_path", lambda source_path: settings.OUTPUT_DIR + "/dummy.js")

    assert compiler.get_full_output_path("dummy.coffee") == os.path.join(settings.ROOT, settings.OUTPUT_DIR, "dummy.js")


def test_get_source_mtime(monkeypatch):

    compiler = compilers.BaseCompiler()

    monkeypatch.setattr(compiler, "get_full_source_path", lambda source_path: "dummy.coffee")
    monkeypatch.setattr("static_precompiler.mtime.get_mtime", lambda filename: 1)

    assert compiler.get_source_mtime("dummy.coffee") == 1


def test_get_output_mtime(monkeypatch):

    compiler = compilers.BaseCompiler()

    monkeypatch.setattr(compiler, "get_full_output_path", lambda output_path: "dummy.js")
    monkeypatch.setattr("os.path.exists", lambda path: False)

    assert compiler.get_output_mtime("dummy.coffee") is None

    monkeypatch.setattr("os.path.exists", lambda path: True)

    monkeypatch.setattr("static_precompiler.mtime.get_mtime", lambda filename: 1)
    assert compiler.get_output_mtime("dummy.coffee") == 1


def test_should_compile(monkeypatch):
    compiler = compilers.BaseCompiler()

    monkeypatch.setattr(compiler, "get_dependencies", lambda source_path: ["B", "C"])

    mtimes = dict(
        A=1,
        B=3,
        C=5,
    )

    monkeypatch.setattr(compiler, "get_source_mtime", lambda x: mtimes[x])
    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: None)

    assert compiler.should_compile("A") is True

    monkeypatch.setattr(compiler, "supports_dependencies", True)

    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: 6)
    assert compiler.should_compile("A") is False

    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: 5)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: 4)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: 2)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr(compiler, "supports_dependencies", False)

    assert compiler.should_compile("A") is False

    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: 1)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr(compiler, "get_output_mtime", lambda x: 0)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.settings.DISABLE_AUTO_COMPILE", True)
    assert compiler.should_compile("A") is False


def test_get_source():
    compiler = compilers.BaseCompiler()
    assert compiler.get_source("scripts/test.coffee") == 'console.log "Hello, World!"'


def test_compile_source():
    compiler = compilers.BaseCompiler()
    with pytest.raises(NotImplementedError):
        compiler.compile_source("source")


def test_compile(monkeypatch):
    compiler = compilers.BaseCompiler()

    monkeypatch.setattr(compiler, "compile_file", pretend.call_recorder(lambda *args: "dummy.js"))
    monkeypatch.setattr(compiler, "update_dependencies", pretend.call_recorder(lambda *args: None))
    monkeypatch.setattr(compiler, "find_dependencies", pretend.call_recorder(lambda *args: ["A", "B"]))
    monkeypatch.setattr(compiler, "get_output_path", lambda *args: "dummy.js")
    monkeypatch.setattr(compiler, "is_supported", lambda *args: False)
    monkeypatch.setattr(compiler, "should_compile", lambda *args, **kwargs: True)

    with pytest.raises(ValueError):
        compiler.compile("dummy.coffee")

    # noinspection PyUnresolvedReferences
    assert compiler.compile_file.calls == []

    monkeypatch.setattr(compiler, "is_supported", lambda *args: True)
    monkeypatch.setattr(compiler, "should_compile", lambda *args, **kwargs: False)

    assert compiler.compile("dummy.coffee") == "dummy.js"
    # noinspection PyUnresolvedReferences
    assert compiler.compile_file.calls == []

    monkeypatch.setattr(compiler, "should_compile", lambda *args, **kwargs: True)
    assert compiler.compile("dummy.coffee") == "dummy.js"

    # noinspection PyUnresolvedReferences
    assert compiler.compile_file.calls == [pretend.call("dummy.coffee")]

    # noinspection PyUnresolvedReferences
    assert compiler.update_dependencies.calls == []

    monkeypatch.setattr(compiler, "supports_dependencies", True)
    compiler.supports_dependencies = True
    compiler.compile("dummy.coffee")
    # noinspection PyUnresolvedReferences
    assert compiler.find_dependencies.calls == [pretend.call("dummy.coffee")]
    # noinspection PyUnresolvedReferences
    assert compiler.update_dependencies.calls == [pretend.call("dummy.coffee", ["A", "B"])]


def test_compile_lazy(monkeypatch):
    compiler = compilers.BaseCompiler()

    monkeypatch.setattr(compiler, "compile", pretend.call_recorder(lambda path: path))

    lazy_compiled = compiler.compile_lazy("dummy.coffee")
    # noinspection PyUnresolvedReferences
    assert compiler.compile.calls == []

    assert encoding.force_text(lazy_compiled) == "dummy.coffee"

    # noinspection PyUnresolvedReferences
    assert compiler.compile.calls == [pretend.call("dummy.coffee")]

    assert compiler.compile(encoding.force_text("foo")).startswith(encoding.force_text("")) is True
    assert compiler.compile(encoding.force_bytes("foo")).startswith(encoding.force_bytes("")) is True


def test_find_dependencies():
    compiler = compilers.BaseCompiler()
    assert compiler.find_dependencies("dummy.coffee") == []


@pytest.mark.django_db
def test_get_dependencies(monkeypatch):
    compiler = compilers.BaseCompiler()

    assert models.Dependency.objects.exists() is False

    assert compiler.get_dependencies("spam.scss") == []

    dependency_1 = models.Dependency.objects.create(
        source="spam.scss",
        depends_on="ham.scss"
    )
    dependency_2 = models.Dependency.objects.create(
        source="spam.scss",
        depends_on="eggs.scss"
    )

    def get_full_source_path(source_path):
        # File "eggs.scss" does not exist
        if source_path == "eggs.scss":
            raise ValueError()
        return source_path

    monkeypatch.setattr(compiler, "get_full_source_path", get_full_source_path)

    assert list(models.Dependency.objects.all()) == [dependency_1, dependency_2]

    assert compiler.get_dependencies("spam.scss") == ["ham.scss"]

    # Dependency the refers to non-existing file were removed.
    assert list(models.Dependency.objects.all()) == [dependency_1]


@pytest.mark.django_db
def test_get_dependents(monkeypatch):
    compiler = compilers.BaseCompiler()

    assert not models.Dependency.objects.exists()

    assert compiler.get_dependents("spam.scss") == []

    dependency_1 = models.Dependency.objects.create(
        source="ham.scss",
        depends_on="spam.scss"
    )
    dependency_2 = models.Dependency.objects.create(
        source="eggs.scss",
        depends_on="spam.scss"
    )

    def get_full_source_path(source_path):
        # File "eggs.scss" does not exist
        if source_path == "eggs.scss":
            raise ValueError()
        return source_path

    monkeypatch.setattr(compiler, "get_full_source_path", get_full_source_path)

    assert list(models.Dependency.objects.all()) == [dependency_1, dependency_2]

    assert compiler.get_dependents("spam.scss") == ["ham.scss"]

    # Dependency the refers to non-existing file were removed.
    assert list(models.Dependency.objects.all()) == [dependency_1]


@pytest.mark.django_db
def test_update_dependencies():
    compiler = compilers.BaseCompiler()

    assert not models.Dependency.objects.exists()

    compiler.update_dependencies("A", ["B", "C"])
    assert sorted(models.Dependency.objects.values_list("source", "depends_on")) == [("A", "B"), ("A", "C")]

    compiler.update_dependencies("A", ["B", "C", "D"])
    assert sorted(models.Dependency.objects.values_list("source", "depends_on")) == [("A", "B"), ("A", "C"), ("A", "D")]

    compiler.update_dependencies("A", ["E"])
    assert sorted(models.Dependency.objects.values_list("source", "depends_on")) == [("A", "E")]

    compiler.update_dependencies("B", ["C"])
    assert sorted(models.Dependency.objects.values_list("source", "depends_on")) == [("A", "E"), ("B", "C")]

    compiler.update_dependencies("A", [])
    assert sorted(models.Dependency.objects.values_list("source", "depends_on")) == [("B", "C")]
