from django.core.management import call_command
from static_precompiler.management.commands.compilestatic import get_scanned_dirs
from static_precompiler.settings import STATIC_ROOT, ROOT, OUTPUT_DIR
import pytest
import os


def test_get_scanned_dirs():

    assert get_scanned_dirs() == sorted([
        os.path.join(os.path.dirname(__file__), "staticfiles_dir"),
        os.path.join(os.path.dirname(__file__), "staticfiles_dir_with_prefix"),
        STATIC_ROOT
    ])


@pytest.mark.django_db
def test_compilestatic_command():

    call_command("compilestatic")

    output_path = os.path.join(ROOT, OUTPUT_DIR)

    compiled_files = []
    for root, dirs, files in os.walk(output_path):
        for filename in files:
            compiled_files.append(os.path.join(root[len(output_path):].lstrip("/"), filename))
    compiled_files.sort()

    assert compiled_files == [
        'another_test.js',
        'scripts/test.js',
        'styles/imported.css',
        'styles/test.css',
        'test-compass.css',
    ]
