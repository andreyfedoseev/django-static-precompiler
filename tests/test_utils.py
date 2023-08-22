import os

from pytest_mock import MockFixture

from static_precompiler import utils
from static_precompiler.compilers import BaseCompiler


def test_write_read_file(tmpdir, settings):
    settings.FILE_CHARSET = "utf-8"
    path = os.path.join(tmpdir.dirname, "foo.txt")
    utils.write_file("Привет, Мир!", path)

    assert os.path.exists(path)
    read_content = utils.read_file(path)
    assert isinstance(read_content, str)
    assert read_content == "Привет, Мир!"


def test_compile_static(mocker: MockFixture):
    compiler = mocker.MagicMock(spec=BaseCompiler)
    compiler.compile.return_value = "compiled"
    compiler.compile_lazy.return_value = "compiled lazy"

    mocker.patch("static_precompiler.registry.get_compiler_by_path", return_value=compiler)

    assert utils.compile_static("foo") == "compiled"
    assert utils.compile_static_lazy("foo") == "compiled lazy"
