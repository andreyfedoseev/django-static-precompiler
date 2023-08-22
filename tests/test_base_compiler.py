import os

import pytest
from django.utils import encoding
from pytest_mock import MockFixture

from static_precompiler import compilers, models, settings


def test_is_supported(mocker: MockFixture):
    mocker.patch("static_precompiler.compilers.base.BaseCompiler.input_extension", "foo")
    compiler = compilers.BaseCompiler()

    assert compiler.is_supported("test.foo") is True
    assert compiler.is_supported("test.bar") is False
    assert compiler.is_supported("foo.test") is False


def test_get_output_filename(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    mocker.patch.object(compiler, "input_extension", "coffee")
    mocker.patch.object(compiler, "output_extension", "js")

    assert compiler.get_output_filename("dummy.coffee") == "dummy.js"
    assert compiler.get_output_filename("dummy.coffee.coffee") == "dummy.coffee.js"


def test_get_full_source_path():
    compiler = compilers.BaseCompiler()

    root = os.path.dirname(__file__)

    assert compiler.get_full_source_path("scripts/test.coffee") == os.path.join(
        root, "static", "scripts", "test.coffee"
    )

    with pytest.raises(ValueError):
        compiler.get_full_source_path("scripts/does-not-exist.coffee")

    assert compiler.get_full_source_path("another_test.coffee") == os.path.normpath(
        os.path.join(root, "staticfiles_dir", "another_test.coffee")
    )

    assert compiler.get_full_source_path("prefix/another_test.coffee") == os.path.normpath(
        os.path.join(root, "staticfiles_dir_with_prefix", "another_test.coffee")
    )


def test_get_output_path(mocker: MockFixture):
    compiler = compilers.BaseCompiler()
    mocker.patch.object(
        compiler, "get_output_filename", side_effect=lambda source_path: source_path.replace(".coffee", ".js")
    )

    assert compiler.get_output_path("scripts/test.coffee") == settings.OUTPUT_DIR + "/scripts/test.js"
    assert compiler.get_output_path("/scripts/test.coffee") == settings.OUTPUT_DIR + "/scripts/test.js"


def test_get_full_output_path(mocker: MockFixture):
    compiler = compilers.BaseCompiler()
    mocker.patch.object(compiler, "get_output_path", return_value=settings.OUTPUT_DIR + "/dummy.js")

    assert compiler.get_full_output_path("dummy.coffee") == os.path.join(settings.ROOT, settings.OUTPUT_DIR, "dummy.js")


def test_get_source_mtime(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    mocker.patch.object(compiler, "get_full_source_path", return_value="dummy.coffee")
    mocker.patch("static_precompiler.mtime.get_mtime", return_value=1)

    assert compiler.get_source_mtime("dummy.coffee") == 1


def test_get_output_mtime(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    mocker.patch.object(compiler, "get_full_output_path", return_value="dummy.js")
    mocker.patch("os.path.exists", return_value=False)

    assert compiler.get_output_mtime("dummy.coffee") is None

    mocker.patch("os.path.exists", return_value=True)

    mocker.patch("static_precompiler.mtime.get_mtime", return_value=1)
    assert compiler.get_output_mtime("dummy.coffee") == 1


def test_should_compile(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    mocker.patch.object(compiler, "get_dependencies", return_value=["B", "C"])

    mtimes = {
        "A": 1,
        "B": 3,
        "C": 5,
    }

    mocker.patch.object(compiler, "get_source_mtime", side_effect=lambda x: mtimes[x])
    mocker.patch.object(compiler, "get_output_mtime", return_value=None)

    assert compiler.should_compile("A") is True

    mocker.patch.object(compiler, "supports_dependencies", True)

    mocker.patch.object(compiler, "get_output_mtime", return_value=6)
    assert compiler.should_compile("A") is False

    mocker.patch.object(compiler, "get_output_mtime", return_value=5)
    assert compiler.should_compile("A") is True

    mocker.patch.object(compiler, "get_output_mtime", return_value=4)
    assert compiler.should_compile("A") is True

    mocker.patch.object(compiler, "get_output_mtime", return_value=2)
    assert compiler.should_compile("A") is True

    mocker.patch.object(compiler, "supports_dependencies", False)

    assert compiler.should_compile("A") is False

    mocker.patch.object(compiler, "get_output_mtime", return_value=1)
    assert compiler.should_compile("A") is True

    mocker.patch.object(compiler, "get_output_mtime", return_value=0)
    assert compiler.should_compile("A") is True

    mocker.patch("static_precompiler.settings.DISABLE_AUTO_COMPILE", True)
    assert compiler.should_compile("A") is False


def test_get_source():
    compiler = compilers.BaseCompiler()
    assert compiler.get_source("scripts/test.coffee") == 'console.log "Hello, World!"\n'


def test_compile_source():
    compiler = compilers.BaseCompiler()
    with pytest.raises(NotImplementedError):
        compiler.compile_source("source")


def test_compile(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    compile_file = mocker.patch.object(compiler, "compile_file", return_value="dummy.js")
    update_dependencies = mocker.patch.object(compiler, "update_dependencies", return_value=None)
    find_dependencies = mocker.patch.object(compiler, "find_dependencies", return_value=["A", "B"])
    mocker.patch.object(compiler, "get_output_path", return_value="dummy.js")
    is_supported = mocker.patch.object(compiler, "is_supported", return_value=False)
    should_compile = mocker.patch.object(compiler, "should_compile", return_value=True)

    with pytest.raises(ValueError):
        compiler.compile("dummy.coffee")

    compile_file.assert_not_called()
    is_supported.return_value = True
    should_compile.return_value = False

    assert compiler.compile("dummy.coffee") == "dummy.js"
    compile_file.assert_not_called()

    should_compile.return_value = True
    assert compiler.compile("dummy.coffee") == "dummy.js"

    compile_file.assert_called_once_with("dummy.coffee")

    update_dependencies.assert_not_called()

    compiler.supports_dependencies = True
    compiler.compile("dummy.coffee")
    find_dependencies.assert_called_once_with("dummy.coffee")
    update_dependencies.assert_called_once_with("dummy.coffee", ["A", "B"])


def test_compile_lazy(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    compile = mocker.patch.object(compiler, "compile", side_effect=lambda x: x)

    lazy_compiled = compiler.compile_lazy("dummy.coffee")
    compile.assert_not_called()

    assert encoding.force_str(lazy_compiled) == "dummy.coffee"
    compile.assert_called_once_with("dummy.coffee")


def test_find_dependencies():
    compiler = compilers.BaseCompiler()
    assert compiler.find_dependencies("dummy.coffee") == []


@pytest.mark.django_db
def test_get_dependencies(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    assert models.Dependency.objects.exists() is False

    assert compiler.get_dependencies("spam.scss") == []

    dependency_1 = models.Dependency.objects.create(source="spam.scss", depends_on="ham.scss")
    dependency_2 = models.Dependency.objects.create(source="spam.scss", depends_on="eggs.scss")

    def get_full_source_path(source_path):
        # File "eggs.scss" does not exist
        if source_path == "eggs.scss":
            raise ValueError()
        return source_path

    mocker.patch.object(compiler, "get_full_source_path", side_effect=get_full_source_path)

    assert list(models.Dependency.objects.all()) == [dependency_1, dependency_2]

    assert compiler.get_dependencies("spam.scss") == ["ham.scss"]

    # The Dependency that refers to non-existing file was removed.
    assert list(models.Dependency.objects.all()) == [dependency_1]


@pytest.mark.django_db
def test_get_dependents(mocker: MockFixture):
    compiler = compilers.BaseCompiler()

    assert not models.Dependency.objects.exists()

    assert compiler.get_dependents("spam.scss") == []

    dependency_1 = models.Dependency.objects.create(source="ham.scss", depends_on="spam.scss")
    dependency_2 = models.Dependency.objects.create(source="eggs.scss", depends_on="spam.scss")

    def get_full_source_path(source_path):
        # File "eggs.scss" does not exist
        if source_path == "eggs.scss":
            raise ValueError()
        return source_path

    mocker.patch.object(compiler, "get_full_source_path", side_effect=get_full_source_path)

    assert list(models.Dependency.objects.all()) == [dependency_1, dependency_2]

    assert compiler.get_dependents("spam.scss") == ["ham.scss"]

    # The Dependency that refers to non-existing file was removed.
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
