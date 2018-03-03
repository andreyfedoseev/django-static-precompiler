************************************
``compilestatic`` management command
************************************

Django Static Precompiler includes a management command ``compilestatic``. It will scan your static files for source
files and compile all of them.

You can use this command in conjunction with ``STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE`` setting if you use custom
``STATICFILES_STORAGE`` such as S3 or some CDN. In that case you can should run ``compilestatic`` every time when your
source files change and then run ``collectstatic``.

Sometimes it may be useful to prevent dependency tracking when running ``compilestatic``, for example when you don't
have access to a database (building a Docker image). Use ``--ignore-dependencies`` option to disable the dependency
tracking.

``--delete-stale-files`` option may be used to delete compiled files that no longer have matching source files.
Example: you have a ``styles.scss`` which get compiled to ``styles.css``. If you remove the source file ``styles.scss``
and run ``compilestatic --delete-stale-files`` it will compile the files as usual, and delete the stale ``styles.css``
file.

You can run ``compilestatic`` in watch mode (``--watch`` option). In watch mode it will monitor the changes in your
source files and re-compile them on the fly. It can be handy if you use tools such as
`LiveReload <http://livereload.com/>`_.

You should install `Watchdog <http://pythonhosted.org/watchdog/>`_ to use watch mode or install ``django-static-precompiler`` with the ``watch`` extra::

    $ pip install django-static-precompiler[watch]


