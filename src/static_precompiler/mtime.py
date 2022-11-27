import os
from typing import Optional

from . import caching, settings


def get_mtime_cachekey(filename: str) -> str:
    return caching.get_cache_key(f"mtime.{caching.get_hexdigest(filename)}")


def get_mtime(filename: str) -> float:
    if settings.MTIME_DELAY:
        key = get_mtime_cachekey(filename)
        cache = caching.get_cache()
        mtime: Optional[float] = cache.get(key)
        if mtime is None:
            mtime = os.path.getmtime(filename)
            cache.set(key, mtime, settings.MTIME_DELAY)
        return mtime
    return os.path.getmtime(filename)
