from django.contrib.staticfiles import finders
from django.core.files import storage

from . import settings


class StaticPrecompilerFileStorage(storage.FileSystemStorage):
    """
    Standard file system storage for files handled by django-static-precompiler.

    The default for ``location`` is ``STATIC_PRECOMPILER_ROOT``
    """
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.ROOT
        super(StaticPrecompilerFileStorage, self).__init__(location, base_url)


class StaticPrecompilerFinder(finders.BaseStorageFinder):
    """
    A staticfiles finder that looks in STATIC_PRECOMPILER_ROOT for compiled files, to be used during development
    with staticfiles development file server or during deployment.
    """
    storage = StaticPrecompilerFileStorage

    def list(self, ignore_patterns):
        if settings.FINDER_LIST_FILES:
            return super(StaticPrecompilerFinder, self).list(ignore_patterns)
        return []
