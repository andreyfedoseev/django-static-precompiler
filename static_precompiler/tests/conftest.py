import os
import shutil

import pytest

from static_precompiler.settings import OUTPUT_DIR, ROOT


@pytest.fixture(autouse=True)
def _no_output_dir(request):
    """ Make sure that output dir does not exists. """

    path = os.path.join(ROOT, OUTPUT_DIR)

    if os.path.exists(path):
        shutil.rmtree(path)

    def fin():
        if os.path.exists(path):
            shutil.rmtree(path)

    request.addfinalizer(fin)
