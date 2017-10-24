import os

import pytest
from django.core import management

import static_precompiler.settings
from static_precompiler.management.commands import compilestatic


def test_get_scanned_dirs():

    assert compilestatic.get_scanned_dirs() == sorted([
        os.path.join(os.path.dirname(__file__), "compilestatic"),
        os.path.join(os.path.dirname(__file__), "staticfiles_dir"),
        os.path.join(os.path.dirname(__file__), "staticfiles_dir_with_prefix"),
        static_precompiler.settings.STATIC_ROOT,
    ])


@pytest.mark.django_db
def test_list_files(capsys, monkeypatch, tmpdir):
    monkeypatch.setattr("static_precompiler.settings.EXCLUDED_FILES", '*/another_test*')

    management.call_command("compilestatic", verbosity=verbosity)

    output_path = os.path.join(tmpdir.strpath, static_precompiler.settings.OUTPUT_DIR)

    compiled_files = []
    for root, dirs, files in os.walk(output_path):
        for filename in files:
            compiled_files.append(os.path.join(root[len(output_path):].lstrip("/"), filename))

    for f in compiled_files:
        assert 'another_test' not in f

    monkeypatch.setattr("static_precompiler.settings.EXCLUDED_FILES", [])
    monkeypatch.setattr("static_precompiler.settings.INCLUDED_FILES", ['*/another_test*'])

    management.call_command("compilestatic", verbosity=verbosity)

    output_path = os.path.join(tmpdir.strpath, static_precompiler.settings.OUTPUT_DIR)

    compiled_files = []
    for root, dirs, files in os.walk(output_path):
        for filename in files:
            compiled_files.append(os.path.join(root[len(output_path):].lstrip("/"), filename))

    for f in compiled_files:
        assert 'another_test' in f


@pytest.mark.django_db
@pytest.mark.parametrize("verbosity", (0, 1, ))
def test_compilestatic_command(verbosity, capsys, monkeypatch, tmpdir):

    monkeypatch.setattr("static_precompiler.management.commands.compilestatic.get_scanned_dirs", lambda: (
        os.path.join(os.path.dirname(__file__), "compilestatic"),
    ))
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    management.call_command("compilestatic", verbosity=verbosity)

    output_path = os.path.join(tmpdir.strpath, static_precompiler.settings.OUTPUT_DIR)

    compiled_files = []
    for root, dirs, files in os.walk(output_path):
        for filename in files:
            compiled_files.append(os.path.join(root[len(output_path):].lstrip("/"), filename))

    compiled_files.sort()

    assert compiled_files == [
        "coffee/test.js",
        "less/test.css",
        "scss/test.css",
    ]

    stdout, _ = capsys.readouterr()

    if verbosity >= 1:
        assert stdout == (
            "Compiled 'coffee/test.coffee' to 'COMPILED/coffee/test.js'\n"
            "Compiled 'less/test.less' to 'COMPILED/less/test.css'\n"
            "Compiled 'scss/test.scss' to 'COMPILED/scss/test.css'\n"
        )
    else:
        assert stdout == ""
