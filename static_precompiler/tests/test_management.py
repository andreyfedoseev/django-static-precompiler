import os

import pytest
from django.core import management

from static_precompiler import settings
from static_precompiler.management.commands import compilestatic


def test_get_scanned_dirs():

    assert compilestatic.get_scanned_dirs() == sorted([
        os.path.join(os.path.dirname(__file__), "staticfiles_dir"),
        os.path.join(os.path.dirname(__file__), "staticfiles_dir_with_prefix"),
        settings.STATIC_ROOT
    ])


@pytest.mark.django_db
def test_compilestatic_command(monkeypatch, tmpdir):

    monkeypatch.setattr("static_precompiler.settings.ROOT", tmpdir.strpath)

    management.call_command("compilestatic")

    output_path = os.path.join(tmpdir.strpath, settings.OUTPUT_DIR)

    compiled_files = []
    for root, dirs, files in os.walk(output_path):
        for filename in files:
            compiled_files.append(os.path.join(root[len(output_path):].lstrip("/"), filename))
    compiled_files.sort()

    assert compiled_files == [
        "another_test.js",
        "scripts/test.js",
        "styles/imported.css",
        "styles/stylus/A.css",
        "styles/stylus/B/C.css",
        "styles/stylus/D.css",
        "styles/stylus/E/F.css",
        "styles/stylus/E/index.css",
        "styles/test.css",
        "test-compass.css",
    ]
