from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os


STATIC_ROOT = getattr(settings, "STATIC_ROOT", getattr(settings, "MEDIA_ROOT"))
STATIC_URL = getattr(settings, "STATIC_URL", getattr(settings, "MEDIA_URL"))

POSIX_COMPATIBLE = True if os.name == 'posix' else False

MTIME_DELAY = getattr(settings, "STATIC_PRECOMPILER_MTIME_DELAY", 10)  # 10 seconds

COMPILERS = getattr(settings, "STATIC_PRECOMPILER_COMPILERS", (
    "static_precompiler.compilers.CoffeeScript",
    "static_precompiler.compilers.SASS",
    "static_precompiler.compilers.SCSS",
    "static_precompiler.compilers.LESS",
))

ROOT = getattr(settings, "STATIC_PRECOMPILER_ROOT",
               getattr(settings, "STATIC_ROOT",
                       getattr(settings, "MEDIA_ROOT")))

if not ROOT:
    raise ImproperlyConfigured("You must specify either STATIC_ROOT or STATIC_PRECOMPILER_ROOT folder.")


OUTPUT_DIR = getattr(settings, "STATIC_PRECOMPILER_OUTPUT_DIR",
                     "COMPILED")

# Use cache for inline compilation
USE_CACHE = getattr(settings, "STATIC_PRECOMPILER_USE_CACHE", True)

# Cache timeout for inline compilation
CACHE_TIMEOUT = getattr(
    settings,
    "STATIC_PRECOMPILER_CACHE_TIMEOUT",
    60 * 60 * 24 * 30
)  # 30 days

# Name of the cache
CACHE_NAME = getattr(settings, "STATIC_PRECOMPILER_CACHE_NAME", None)

COFFEESCRIPT_EXECUTABLE = getattr(settings, "COFFEESCRIPT_EXECUTABLE", "coffee")
SCSS_EXECUTABLE = getattr(settings, "SCSS_EXECUTABLE", "sass")
SCSS_USE_COMPASS = getattr(settings, "SCSS_USE_COMPASS", False)
LESS_EXECUTABLE = getattr(settings, "LESS_EXECUTABLE", "lessc")

PREPEND_STATIC_URL = getattr(settings, 'STATIC_PRECOMPILER_PREPEND_STATIC_URL', False)

DISABLE_AUTO_COMPILE = getattr(settings, 'STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE', False)
