=========================
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/andreyfedoseev/django-static-precompiler?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
Django Static Precompiler
=========================

Django Static Precompiler provides template tags to compile CoffeeScript, SASS / SCSS and LESS.
It works with both inline code and external files.

.. image:: https://travis-ci.org/andreyfedoseev/django-static-precompiler.svg?branch=master
   :target: https://travis-ci.org/andreyfedoseev/django-static-precompiler
   :alt: Build Status

Installation
============

1. Add "static_precompiler" to INSTALLED_APPS setting.
2. Initialize DB:

   * On Django < 1.7 run ``syncdb`` or ``migrate static_precompiler`` if you use South (1.0 is required).
   * On Django >= 1.7 run ``migrate static_precompiler``.

3. Make sure that you have necessary compilers installed.
4. Optionally, you can specify the full path to compilers (for example ``SCSS_EXECUTABLE='/usr/local/bin/sass'``).
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
Compiler needs to be specified in ``STATIC_PRECOMPILER_COMPILERS`` settings. Names for default compilers are:

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
    {% endinlinecoffeescript %}
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
        'static_precompiler.compilers.SASS',
        'static_precompiler.compilers.SCSS',
        'static_precompiler.compilers.LESS',
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
  only with ``compilestatic`` command (see below).

Compiler specific settings
================

CoffeeScript
------------

``COFFEESCRIPT_EXECUTABLE``
  Path to CoffeeScript compiler executable. Default: ``"coffee"``.

SASS / SCSS
-----------

``SCSS_EXECUTABLE``
  Path to SASS compiler executable. Default: "sass".

``SCSS_USE_COMPASS``
  Boolean. Wheter to use compass or not. Compass must be installed in your system. Run "sass --compass" and if no error is shown it means that compass is installed.

LESS
----

``LESS_EXECUTABLE``
  Path to LESS compiler executable. Default: ``"lessc"``.

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
