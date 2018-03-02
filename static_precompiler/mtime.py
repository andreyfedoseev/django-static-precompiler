import os

from . import settings, caching


def get_mtime_cachekey(filename):
    return caching.get_cache_key("mtime.{0}".format(caching.get_hexdigest(filename)))


def get_mtime(filename):
    if settings.MTIME_DELAY:
        key = get_mtime_cachekey(filename)
        cache = caching.get_cache()
        mtime = cache.get(key)
        if mtime is None:
            mtime = os.path.getmtime(filename)
            cache.set(key, mtime, settings.MTIME_DELAY)
        return mtime
    return os.path.getmtime(filename)
