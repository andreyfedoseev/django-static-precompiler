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

    tree = [(root[len(output_path):], dirs, files) for root, dirs, files in os.walk(output_path)]

    assert tree == [('', ['scripts', 'styles'], ['another_test.js', 'test-compass.css']),
                    ('/scripts', [], ['test.js']),
                    ('/styles', [], ['imported.css', 'test.css'])]
