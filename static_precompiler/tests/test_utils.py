# coding: utf-8
from __future__ import unicode_literals

import os

from django.utils import six
from pretend import stub

from static_precompiler import utils


def test_write_read_file(tmpdir, settings):
    settings.FILE_CHARSET = "utf-8"
    path = os.path.join(tmpdir.dirname, "foo.txt")
    utils.write_file("Привет, Мир!", path)

    assert os.path.exists(path)
    read_content = utils.read_file(path)
    assert isinstance(read_content, six.text_type)
    assert read_content == "Привет, Мир!"


def test_compile_static(monkeypatch):

    compiler_stub = stub(
        compile=lambda x: "compiled",
        compile_lazy=lambda x: "compiled lazy"
    )

    monkeypatch.setattr("static_precompiler.registry.get_compiler_by_path", lambda path: compiler_stub)

    assert utils.compile_static("foo") == "compiled"
    assert utils.compile_static_lazy("foo") == "compiled lazy"
