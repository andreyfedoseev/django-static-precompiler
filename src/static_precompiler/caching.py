import hashlib
import socket
from typing import Optional

import django.core.cache
import django.utils.encoding
from django.core.cache import BaseCache

from . import settings


def get_cache() -> BaseCache:
    if settings.CACHE_NAME:
        return django.core.cache.caches.get(settings.CACHE_NAME)  # type: ignore
    return django.core.cache.cache  # type: ignore


def get_cache_key(key: str) -> str:
    return f"static_precompiler.{socket.gethostname()}.{key}"


def get_hexdigest(plaintext: str, length: Optional[int] = None) -> str:
    digest = hashlib.md5(django.utils.encoding.smart_bytes(plaintext)).hexdigest()
    if length:
        return digest[:length]
    return digest
