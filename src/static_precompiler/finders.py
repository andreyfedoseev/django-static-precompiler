from typing import Any, Iterable, Optional

from django.contrib.staticfiles import finders
from django.core.files import storage

from . import settings
from .types import StrCollection


class StaticPrecompilerFileStorage(storage.FileSystemStorage):
    """
    Standard file system storage for files handled by django-static-precompiler.

    The default for ``location`` is ``STATIC_PRECOMPILER_ROOT``
    """

    def __init__(self, location: Optional[str] = None, base_url: Optional[str] = None):
        if location is None:
            location = settings.ROOT
        super().__init__(location, base_url)


class StaticPrecompilerFinder(finders.BaseStorageFinder):
    """
    A staticfiles finder that looks in STATIC_PRECOMPILER_ROOT for compiled files, to be used during development
    with staticfiles development file server or during deployment.
    """

    storage = StaticPrecompilerFileStorage  # type: ignore

    def list(self, ignore_patterns: Optional[StrCollection]) -> Iterable[Any]:
        if settings.FINDER_LIST_FILES:
            return super().list(ignore_patterns)
        return []
