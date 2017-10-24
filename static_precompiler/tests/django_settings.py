import os

DEBUG = True
SECRET_KEY = "static_precompiler"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

STATIC_ROOT = MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = MEDIA_URL = "/static/"

# noinspection PyUnresolvedReferences
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'compilestatic'),
    os.path.join(os.path.dirname(__file__), 'staticfiles_dir'),
    ("prefix", os.path.join(os.path.dirname(__file__), 'staticfiles_dir_with_prefix')),
)

INSTALLED_APPS = (
    "static_precompiler",
)
MTIME_DELAY = 2

STATIC_PRECOMPILER_USE_CACHE = False
