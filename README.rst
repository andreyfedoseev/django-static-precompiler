=========================
Django Static Precompiler
=========================

Django Static Precompiler provides template tags to compile CoffeeScript, SASS / SCSS and LESS.
It works with both inline code and external files.

.. image:: https://travis-ci.org/andreyfedoseev/django-static-precompiler.svg?branch=master
   :target: https://travis-ci.org/andreyfedoseev/django-static-precompiler
   :alt: Build Status

.. image:: https://badges.gitter.im/Join Chat.svg
    :target: https://gitter.im/andreyfedoseev/django-static-precompiler?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
    :alt: Gitter

Installation
============

1. Add "static_precompiler" to INSTALLED_APPS setting.
2. Initialize DB:

   * On Django < 1.7 run ``syncdb`` or ``migrate static_precompiler`` if you use South (1.0 is required).
   * On Django >= 1.7 run ``migrate static_precompiler``.

3. Make sure that you have necessary compilers installed.
4. Optionally, you can specify the full path to compilers (see below).
5. In case you use Django’s staticfiles contrib app you have to add static-precompiler’s file finder to the ``STATICFILES_FINDERS`` setting, for example::

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        # other finders..
        'static_precompiler.finders.StaticPrecompilerFinder',
    )

Note that by default compiled files are saved into ``COMPILED`` folder under your ``STATIC_ROOT`` (or ``MEDIA_ROOT`` if you have no ``STATIC_ROOT`` in your settings).
You can change this folder with ``STATIC_PRECOMPILER_ROOT`` and ``STATIC_PRECOMPILER_OUTPUT_DIR`` settings.

Note that all relative URLs in your stylesheets are converted to absolute URLs using your ``STATIC_URL`` setting.

{% compile %} tag
=================

``{% compile %}`` is a template tag that allows to compile any source file supported by compilers configured with
``STATIC_PRECOMPILER_COMPILERS`` settings.

Example Usage
-------------

::

  {% load compile_static %}

  <script src="{{ STATIC_URL}}{% compile "path/to/script.coffee" %}"></script>
  <link rel="stylesheet" href="{{ STATIC_URL}}{% compile "path/to/styles1.less" %}" />
  <link rel="stylesheet" href="{{ STATIC_URL}}{% compile "path/to/styles2.scss" %}" />

renders to::

  <script src="/static/COMPILED/path/to/script.js"></script>
  <link rel="stylesheet" href="/static/COMPILED/path/to/styles1.css" />
  <link rel="stylesheet" href="/static/COMPILED/path/to/styles2.css" />

{% inlinecompile %} tag
=======================

Compiles everything between ``{% inlinecompile %}`` and ``{% endinlinecompile %}`` with compiler specified by name.
Compiler must be specified in ``STATIC_PRECOMPILER_COMPILERS`` setting. Names for default compilers are:

* ``coffeescript``
* ``less``
* ``sass``
* ``scss``

Example Usage
-------------

::

  {% load compile_static %}

  <script type="text/javascript">
    {% inlinecompile "coffeescript" %}
      console.log "Hello, World!"
    {% endinlinecompile %}
  </script>

renders to::

  <script type="text/javascript">
    (function() {
      console.log("Hello, World!");
    }).call(this);
  </script>

General settings
================

``STATIC_PRECOMPILER_COMPILERS``
  List of enabled compilers. You can modify it to enable your custom compilers. Default::

    STATIC_PRECOMPILER_COMPILERS = (
        'static_precompiler.compilers.CoffeeScript',
        'static_precompiler.compilers.ES6To5',
        'static_precompiler.compilers.SASS',
        'static_precompiler.compilers.SCSS',
        'static_precompiler.compilers.LESS',
    )

  You can specify compiler options using the following format::

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.CoffeeScript', {"executable": "/usr/bin/coffeescript"}),
        ('static_precompiler.compilers.SCSS', {"compass_enabled": True}),
    )


``STATIC_PRECOMPILER_ROOT``
  Controls the absolute file path that compiled files will be written to. Default: ``STATIC_ROOT``.

``STATIC_PRECOMPILER_OUTPUT_DIR``
  Controls the directory inside ``STATIC_PRECOMPILER_ROOT`` that compiled files will be written to. Default: ``"COMPILED"``.

``STATIC_PRECOMPILER_USE_CACHE``
  Whether to use cache for inline compilation. Default: ``True``.

``STATIC_PRECOMPILER_CACHE_TIMEOUT``
  Cache timeout for inline styles (in seconds). Default: 30 days.

``STATIC_PRECOMPILER_MTIME_DELAY``
  Cache timeout for reading the modification time of source files (in seconds). Default: 10 seconds.

``STATIC_PRECOMPILER_CACHE_NAME``
  Name of the cache to be used. If not specified then the default django cache is used. Default: ``None``.

``STATIC_PRECOMPILER_PREPEND_STATIC_URL``
  Add ``STATIC_URL`` to the output of template tags. Default: ``False``

``STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE``
  Disable automatic compilation from template tags or ``compile_static`` utility function. Files are compiled
  only with ``compilestatic`` command (see below). Default:: ``False``

``STATIC_PRECOMPILER_LIST_FILES``
  Whether or not ``static_precompiler.finders.StaticPrecompilerFinder`` will list compiled files when ``collectstatic``
  command is executed. Set to ``True`` if you want compiled files to be found by ``collectstatic``. Default:: ``False``.


Compiler specific settings
==========================

CoffeeScript
------------

``executable``
  Path to CoffeeScript compiler executable. Default: ``"coffee"``.

Example::

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.CoffeeScript', {"executable": "/usr/bin/coffee"}),
    )


6to5
----

``executable``
  Path to 6to5 compiler executable. Default: ``"6to5"``.

Example::

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.ES6To5', {"executable": "/usr/bin/6to5"}),
    )


SASS / SCSS
-----------

``executable``
  Path to SASS compiler executable. Default: "sass".

``compass_enabled``
  Boolean. Wheter to use compass or not. Compass must be installed in your system. Run "sass --compass" and if no error is shown it means that compass is installed.

Example::

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.SCSS', {"executable": "/usr/bin/sass", "compass_enabled": True}),
    )


LESS
----

``executable``
  Path to LESS compiler executable. Default: ``"lessc"``.

Example::

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.less.LESS', {"executable": "/usr/bin/lessc"),
    )


Usage with forms media
======================

If you want to use ``static_precompiler`` in form media definitions, you can use the following approach::

  from django import forms
  from static_precompiler.utils import compile_static

  class MyForm(forms.Form):

      @property
      def media(self):
          return forms.Media(
              css={"all": (
                  compile_static("styles/myform.scss"),
              )},
              js=(
                  compile_static("scripts/myform.coffee"),
              )
          )


``compilestatic`` management command
====================================

Django Static Precompiler includes a management command ``compilestatic``. If will scan your static files for source
files and compile all of them.

You can use this command in conjunction with ``STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE`` setting if you use custom
``STATICFILES_STORAGE`` such as S3 or some CDN. In that case you can should run ``compilestatic`` every time when your
source files change and then run ``collectstatic``.

You can run ``compilestatic`` in watch mode (``--watch`` option). In watch mode it will monitor the changes in your
source files and re-compile them on the fly. It can be handy if you use tools such as
`LiveReload <http://livereload.com/>`_.

You should install `Watchdog <http://pythonhosted.org/watchdog/>`_ to use watch mode.


Troubleshooting
===============

If you get ``[Errno 2] No such file or directory`` make sure that you have the required compiler installed. For all
compilers you can specify the path to executable file using the ``executable`` option, see examples above.

If you run ``migrate`` and get ``ImportError: cannot import name migrations`` then most likely you use Django < 1.7 and
South < 1.0. You should either upgrade to Django 1.7+ or use South 1.0.
