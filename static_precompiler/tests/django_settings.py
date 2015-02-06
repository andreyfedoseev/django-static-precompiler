# noinspection PyUnresolvedReferences
from django.conf.global_settings import *
import os

DEBUG = True
SECRET_KEY = "static_precompiler"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_ROOT = MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = MEDIA_URL = "/static/"

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'staticfiles_dir'),
    ("prefix", os.path.join(os.path.dirname(__file__), 'staticfiles_dir_with_prefix')),
)

INSTALLED_APPS = (
    "static_precompiler",
)
MTIME_DELAY = 2

SCSS_USE_COMPASS = True

LESS_GLOBAL_VARS = [
    ('VAR', 'global-var'),
    ('COLOR', '#ff0000'),
]