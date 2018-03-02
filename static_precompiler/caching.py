import hashlib
import socket

import django.core.cache
import django.utils.encoding

from . import settings


def get_cache():
    if settings.CACHE_NAME:
        return django.core.cache.caches.get(settings.CACHE_NAME)
    return django.core.cache.cache


def get_cache_key(key):
    return "static_precompiler.{0}.{1}".format(socket.gethostname(), key)


def get_hexdigest(plaintext, length=None):
    digest = hashlib.md5(django.utils.encoding.smart_bytes(plaintext)).hexdigest()
    if length:
        return digest[:length]
    return digest
