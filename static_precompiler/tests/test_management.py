from static_precompiler.management.commands.compilestatic import get_scanned_dirs
from static_precompiler.settings import STATIC_ROOT
import os


def test_get_scanned_dirs():

    assert get_scanned_dirs() == sorted([
        os.path.join(os.path.dirname(__file__), "staticfiles_dir"),
        os.path.join(os.path.dirname(__file__), "staticfiles_dir_with_prefix"),
        STATIC_ROOT
    ])
