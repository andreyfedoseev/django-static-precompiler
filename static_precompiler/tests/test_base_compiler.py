from static_precompiler.models import Dependency
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.settings import OUTPUT_DIR, ROOT
from pretend import call_recorder, call
import os
import pytest


def test_is_supported(monkeypatch):

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.input_extension", ".foo")
    compiler = BaseCompiler()

    assert compiler.is_supported("test.foo") is True
    assert compiler.is_supported("test.bar") is False
    assert compiler.is_supported("foo.test") is False


def test_get_output_filename(monkeypatch):

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.input_extension", ".coffee")
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.output_extension", ".js")

    compiler = BaseCompiler()
    assert compiler.get_output_filename("dummy.coffee") == "dummy.js"
    assert compiler.get_output_filename("dummy.coffee.coffee") == "dummy.coffee.js"


def test_get_full_source_path():
    compiler = BaseCompiler()

    root = os.path.dirname(__file__)

    assert compiler.get_full_source_path("scripts/test.coffee") == os.path.join(root, "static", "scripts",
                                                                                "test.coffee")

    with pytest.raises(ValueError):
        compiler.get_full_source_path("scripts/does-not-exist.coffee")

    assert compiler.get_full_source_path("another_test.coffee") == os.path.normpath(
        os.path.join(
            root,
            "staticfiles_dir",
            "another_test.coffee"
        )
    )

    assert compiler.get_full_source_path("prefix/another_test.coffee") == os.path.normpath(
        os.path.join(
            root,
            "staticfiles_dir_with_prefix",
            "another_test.coffee"
        )
    )


def test_get_output_path(monkeypatch):

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_filename",
                        lambda self, source_path: source_path.replace(".coffee", ".js"))

    compiler = BaseCompiler()
    assert compiler.get_output_path("scripts/test.coffee") == OUTPUT_DIR + "/scripts/test.js"


def test_get_full_output_path(monkeypatch):

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_path",
                        lambda self, source_path: OUTPUT_DIR + "/dummy.js")

    compiler = BaseCompiler()
    assert compiler.get_full_output_path("dummy.coffee") == os.path.join(ROOT, OUTPUT_DIR, "dummy.js")


def test_get_source_mtime(monkeypatch):

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_full_source_path",
                        lambda self, source_path: "dummy.coffee")
    monkeypatch.setattr("static_precompiler.compilers.base.get_mtime", lambda filename: 1)

    compiler = BaseCompiler()
    assert compiler.get_source_mtime("dummy.coffee") == 1


def test_get_output_mtime(monkeypatch):

    compiler = BaseCompiler()

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_full_output_path",
                        lambda self, output_path: "dummy.js")
    monkeypatch.setattr("os.path.exists", lambda path: False)

    assert compiler.get_output_mtime("dummy.coffee") is None

    monkeypatch.setattr("os.path.exists", lambda path: True)

    monkeypatch.setattr("static_precompiler.compilers.base.get_mtime", lambda filename: 1)
    assert compiler.get_output_mtime("dummy.coffee") == 1


def test_should_compile(monkeypatch):
    compiler = BaseCompiler()

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_dependencies",
                        lambda self, source_path: ["B", "C"])

    mtimes = dict(
        A=1,
        B=3,
        C=5,
    )

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_source_mtime", lambda self, x: mtimes[x])
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: None)

    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.supports_dependencies", True)

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: 6)
    assert compiler.should_compile("A") is False

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: 5)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: 4)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: 2)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.supports_dependencies", False)

    assert compiler.should_compile("A") is False

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: 1)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_mtime", lambda self, x: 0)
    assert compiler.should_compile("A") is True

    monkeypatch.setattr("static_precompiler.compilers.base.DISABLE_AUTO_COMPILE", True)
    assert compiler.should_compile("A") is False


def test_get_source():
    compiler = BaseCompiler()
    assert compiler.get_source("scripts/test.coffee") == 'console.log "Hello, World!"'


def test_write_output(monkeypatch, tmpdir):
    compiler = BaseCompiler()

    output_path = os.path.join(tmpdir.dirname, "dummy.js")
    assert os.path.exists(output_path) is False

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_full_output_path",
                        lambda self, x: output_path)

    compiler.write_output("compiled", "dummy.coffee")
    assert os.path.exists(output_path) is True

    with open(output_path) as output:
        assert output.read() == "compiled"


def test_compile_source():
    compiler = BaseCompiler()
    with pytest.raises(NotImplementedError):
        compiler.compile_source("source")


def test_postprocess():
    compiler = BaseCompiler()
    assert compiler.postprocess("compiled", "dummy.coffee") == "compiled"


def test_compile(monkeypatch):
    compiler = BaseCompiler()

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.compile_file",
                        call_recorder(lambda self, *args: "compiled"))
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.write_output",
                        call_recorder(lambda self, *args: None))
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.postprocess",
                        call_recorder(lambda self, compiled, source_path: compiled))
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.update_dependencies",
                        call_recorder(lambda self, *args: None))
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.find_dependencies",
                        call_recorder(lambda self, *args: ["A", "B"]))
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.get_output_path", lambda self, *args: "dummy.js")

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.is_supported", lambda self, *args: False)
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.should_compile", lambda self, *args, **kwargs: True)

    with pytest.raises(ValueError):
        compiler.compile("dummy.coffee")

    # noinspection PyUnresolvedReferences
    assert compiler.compile_file.calls == []
    # noinspection PyUnresolvedReferences
    assert compiler.write_output.calls == []
    # noinspection PyUnresolvedReferences
    assert compiler.postprocess.calls == []

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.is_supported", lambda self, *args: True)
    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.should_compile", lambda self, *args, **kwargs: False)

    assert compiler.compile("dummy.coffee") == "dummy.js"
    # noinspection PyUnresolvedReferences
    assert compiler.compile_file.calls == []
    # noinspection PyUnresolvedReferences
    assert compiler.write_output.calls == []
    # noinspection PyUnresolvedReferences
    assert compiler.postprocess.calls == []

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.should_compile", lambda self, *args, **kwargs: True)
    assert compiler.compile("dummy.coffee") == "dummy.js"

    # noinspection PyUnresolvedReferences
    assert compiler.compile_file.calls == [call(compiler, "dummy.coffee")]
    # noinspection PyUnresolvedReferences
    assert compiler.write_output.calls == [call(compiler, "compiled", "dummy.coffee")]
    # noinspection PyUnresolvedReferences
    assert compiler.postprocess.calls == [call(compiler, "compiled", "dummy.coffee")]

    # noinspection PyUnresolvedReferences
    assert compiler.update_dependencies.calls == []

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.supports_dependencies", True)
    compiler.supports_dependencies = True
    compiler.compile("dummy.coffee")
    # noinspection PyUnresolvedReferences
    assert compiler.find_dependencies.calls == [call(compiler, "dummy.coffee")]
    # noinspection PyUnresolvedReferences
    assert compiler.update_dependencies.calls == [call(compiler, "dummy.coffee", ["A", "B"])]


def test_compile_lazy(monkeypatch):
    compiler = BaseCompiler()

    monkeypatch.setattr("static_precompiler.compilers.base.BaseCompiler.compile",
                        call_recorder(lambda self, *args: "dummy.js"))

    lazy_compiled = compiler.compile_lazy("dummy.coffee")
    # noinspection PyUnresolvedReferences
    assert compiler.compile.calls == []

    assert str(lazy_compiled) == "dummy.js"

    # noinspection PyUnresolvedReferences
    assert compiler.compile.calls == [call(compiler, "dummy.coffee")]


def test_find_dependencies():
    compiler = BaseCompiler()
    assert compiler.find_dependencies("dummy.coffee") == []


@pytest.mark.django_db
def test_get_dependencies():
    compiler = BaseCompiler()

    assert Dependency.objects.exists() is False

    assert compiler.get_dependencies("spam.scss") == []

    Dependency.objects.create(
        source="spam.scss",
        depends_on="ham.scss"
    )
    Dependency.objects.create(
        source="spam.scss",
        depends_on="eggs.scss"
    )

    assert compiler.get_dependencies("spam.scss") == ["eggs.scss", "ham.scss"]


@pytest.mark.django_db
def test_get_dependents():
    compiler = BaseCompiler()

    assert Dependency.objects.exists() is False

    assert compiler.get_dependents("spam.scss") == []

    Dependency.objects.create(
        source="ham.scss",
        depends_on="spam.scss"
    )
    Dependency.objects.create(
        source="eggs.scss",
        depends_on="spam.scss"
    )

    assert compiler.get_dependents("spam.scss") == ["eggs.scss", "ham.scss"]


@pytest.mark.django_db
def test_update_dependencies():
    compiler = BaseCompiler()

    assert Dependency.objects.exists() is False

    compiler.update_dependencies("A", ["B", "C"])
    assert sorted(Dependency.objects.values_list("source", "depends_on")) == [("A", "B"), ("A", "C")]

    compiler.update_dependencies("A", ["B", "C", "D"])
    assert sorted(Dependency.objects.values_list("source", "depends_on")) == [("A", "B"), ("A", "C"), ("A", "D")]

    compiler.update_dependencies("A", ["E"])
    assert sorted(Dependency.objects.values_list("source", "depends_on")) == [("A", "E")]

    compiler.update_dependencies("B", ["C"])
    assert sorted(Dependency.objects.values_list("source", "depends_on")) == [("A", "E"), ("B", "C")]

    compiler.update_dependencies("A", [])
    assert sorted(Dependency.objects.values_list("source", "depends_on")) == [("B", "C")]
