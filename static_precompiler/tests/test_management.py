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


@pytest.mark.skip("Re-enable when pytest-django>3.1.2 is released")
@pytest.mark.django_db
def test_ignore_dependencies_option(django_assert_num_queries, monkeypatch, tmpdir):

    monkeypatch.setattr("static_precompiler.management.commands.compilestatic.get_scanned_dirs", lambda: (
        os.path.join(os.path.dirname(__file__), "compilestatic"),
    ))
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    with django_assert_num_queries(0):
        management.call_command("compilestatic", ignore_dependencies=True)


@pytest.mark.django_db
def test_delete_stale_files(monkeypatch, tmpdir):

    output_path = os.path.join(tmpdir.strpath, static_precompiler.settings.OUTPUT_DIR)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    unmanaged_file = os.path.join(tmpdir.strpath, "unmanaged.js")
    with open(unmanaged_file, "w+") as f:
        f.write("unmanaged")

    with open(os.path.join(output_path, "stale.js"), "w+") as f:
        f.write("stale")

    monkeypatch.setattr("static_precompiler.management.commands.compilestatic.get_scanned_dirs", lambda: (
        os.path.join(os.path.dirname(__file__), "compilestatic"),
    ))
    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    management.call_command("compilestatic", delete_stale_files=True)

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

    # Files outside of `COMPILED` directory are untouched
    assert os.path.exists(unmanaged_file)
