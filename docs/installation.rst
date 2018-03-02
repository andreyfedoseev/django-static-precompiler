************
Installation
************

``django-static-precompiler`` is avaiable through `pip <http://pypi.python.org/pypi/pip/>`_:

.. code-block:: sh

    $ pip install django-static-precompiler

1. Add "static_precompiler" to INSTALLED_APPS setting.
2. Run ``migrate static_precompiler``.
3. Make sure that you have necessary compilers installed.
4. Optionally, you can specify the full path to compilers (see below).
5. In case you use Django’s staticfiles contrib app you have to add static-precompiler’s file finder to the ``STATICFILES_FINDERS`` setting, for example:

   .. code-block:: python

       STATICFILES_FINDERS = (
           'django.contrib.staticfiles.finders.FileSystemFinder',
           'django.contrib.staticfiles.finders.AppDirectoriesFinder',
           # other finders..
           'static_precompiler.finders.StaticPrecompilerFinder',
       )

Note that by default compiled files are saved into ``COMPILED`` folder under your ``STATIC_ROOT`` (or ``MEDIA_ROOT`` if you have no ``STATIC_ROOT`` in your settings).
You can change this folder with ``STATIC_PRECOMPILER_ROOT`` and ``STATIC_PRECOMPILER_OUTPUT_DIR`` settings.

Note that all relative URLs in your stylesheets are converted to absolute URLs using your ``STATIC_URL`` setting.

