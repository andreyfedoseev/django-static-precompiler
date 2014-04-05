from django.contrib.staticfiles.finders import BaseStorageFinder
from django.core.files.storage import FileSystemStorage
from static_precompiler.settings import ROOT


class StaticPrecompilerFileStorage(FileSystemStorage):
    """
    Standard file system storage for files handled by django-static-precompiler.

    The default for ``location`` is ``STATIC_PRECOMPILER_ROOT``
    """
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = ROOT
        super(StaticPrecompilerFileStorage, self).__init__(location, base_url)


class StaticPrecompilerFinder(BaseStorageFinder):
    """
    A staticfiles finder that looks in STATIC_PRECOMPILER_ROOT
    for compiled files, to be used during development
    with staticfiles development file server or during
    deployment.
    """
    storage = StaticPrecompilerFileStorage

    def list(self, ignore_patterns):
        return []
