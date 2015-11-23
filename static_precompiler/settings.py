import os
import warnings

import django.core.exceptions
from django.conf import settings

STATIC_ROOT = getattr(settings, "STATIC_ROOT", getattr(settings, "MEDIA_ROOT"))
STATIC_URL = getattr(settings, "STATIC_URL", getattr(settings, "MEDIA_URL"))

POSIX_COMPATIBLE = True if os.name == 'posix' else False

MTIME_DELAY = getattr(settings, "STATIC_PRECOMPILER_MTIME_DELAY", 10)  # 10 seconds

COMPILERS = getattr(settings, "STATIC_PRECOMPILER_COMPILERS", (
    "static_precompiler.compilers.CoffeeScript",
    "static_precompiler.compilers.Babel",
    "static_precompiler.compilers.Handlebars",
    "static_precompiler.compilers.SASS",
    "static_precompiler.compilers.SCSS",
    "static_precompiler.compilers.LESS",
    "static_precompiler.compilers.Stylus",
    "static_precompiler.compilers.LiveScript",
))

ROOT = getattr(settings, "STATIC_PRECOMPILER_ROOT",
               getattr(settings, "STATIC_ROOT",
                       getattr(settings, "MEDIA_ROOT")))

if not ROOT:
    raise django.core.exceptions.ImproperlyConfigured(
        "You must specify either STATIC_ROOT or STATIC_PRECOMPILER_ROOT folder."
    )


OUTPUT_DIR = getattr(settings, "STATIC_PRECOMPILER_OUTPUT_DIR", "COMPILED")

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


for deprecated_setting in (
    "COFFEESCRIPT_EXECUTABLE",
    "SCSS_EXECUTABLE",
    "SCSS_USE_COMPASS",
    "LESS_EXECUTABLE",
):
    if hasattr(settings, deprecated_setting):
        warnings.warn(DeprecationWarning("{0} setting is deprecated. Use STATIC_PRECOMPILER_COMPILERS to set compiler "
                                         "options.".format(deprecated_setting)))


COFFEESCRIPT_EXECUTABLE = getattr(settings, "COFFEESCRIPT_EXECUTABLE", "coffee")
SCSS_EXECUTABLE = getattr(settings, "SCSS_EXECUTABLE", "sass")
SCSS_USE_COMPASS = getattr(settings, "SCSS_USE_COMPASS", False)
LESS_EXECUTABLE = getattr(settings, "LESS_EXECUTABLE", "lessc")

PREPEND_STATIC_URL = getattr(settings, 'STATIC_PRECOMPILER_PREPEND_STATIC_URL', False)

DISABLE_AUTO_COMPILE = getattr(settings, 'STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE', False)
FINDER_LIST_FILES = getattr(settings, 'STATIC_PRECOMPILER_FINDER_LIST_FILES', False)
