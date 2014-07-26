=========================
Django Static Precompiler
=========================

Django Static Precompiler provides template tags to compile CoffeeScript, SASS / SCSS and LESS.
It works with both inline code and extenal files.

.. image:: https://travis-ci.org/andreyfedoseev/django-static-precompiler.svg?branch=master
   :target: https://travis-ci.org/andreyfedoseev/django-static-precompiler
   :alt: Build Status

Installation
============

1. Add "static_precompiler" to INSTALLED_APPS setting.
2. Run ``syncdb`` or ``migrate static_precompiler`` if you use South.
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

{% compile %} tag
=================

``{% compile %}`` is a template tag that allows to compile any source file supported by compilers configured with
``STATIC_PRECOMPILER_COMPILERS`` settings. For example::

  {% load compile_static %}

  <script src="{{ STATIC_URL}}{% compile "path/to/script.coffee" %}"></script>
  <link rel="stylesheet" href="{{ STATIC_URL}}{% compile "path/to/styles1.less" %}" />
  <link rel="stylesheet" href="{{ STATIC_URL}}{% compile "path/to/styles2.scss" %}" />

renders to::

  <script src="/static/COMPILED/path/to/script.js"></script>
  <link rel="stylesheet" href="/static/COMPILED/path/to/styles1.css" />
  <link rel="stylesheet" href="/static/COMPILED/path/to/styles2.css" />


CoffeeScript
============

Settings
--------

``COFFEESCRIPT_EXECUTABLE``
  Path to CoffeeScript compiler executable. Default: ``"coffee"``.

Example Usage
-------------

Inline CoffeeScript::

  {% load coffeescript %}

  <script type="text/javascript">
    {% inlinecoffeescript %}
      console.log "Hello, World!"
    {% endinlinecoffeescript %}
  </script>

renders to::

  <script type="text/javascript">
    (function() {
      console.log("Hello, World!");
    }).call(this);
  </script>

External file::

  {% load coffeescript %}

  <script src="{{ STATIC_URL}}{% coffeescript "path/to/script.coffee" %}"></script>

renders to::

  <script src="/static/COMPILED/path/to/script.js"></script>


SASS / SCSS
===========

Settings
--------

``SCSS_EXECUTABLE``
  Path to SASS compiler executable. Default: "sass".

``SCSS_USE_COMPASS``
  Boolean. Wheter to use compass or not. Compass must be installed in your system. Run "sass --compass" and if no error is shown it means that compass is installed.

Example Usage
-------------

Inline SCSS::

  {% load scss %}

  <style>
    {% inlinescss %}
      #header {
        h1 {
          font-size: 26px;
          font-weight: bold;
        }
        p { font-size: 12px;
          a { text-decoration: none;
            &:hover { border-width: 1px }
          }
        }
      }
    {% endinlinescss %}
  </style>

renders to::

  <style>
    #header h1 {
      font-size: 26px;
      font-weight: bold; }
    #header p {
      font-size: 12px; }
      #header p a {
        text-decoration: none; }
        #header p a:hover {
          border-width: 1px; }
  </style>

External file::

  {% load scss %}

  <link rel="stylesheet" href="{{ STATIC_URL}}{% scss "path/to/styles.scss" %}" />

renders to::

  <link rel="stylesheet" href="/static/COMPILED/path/to/styles.css" />


LESS
====

Settings
--------

``LESS_EXECUTABLE``
  Path to LESS compiler executable. Default: ``"lessc"``.

Example Usage
-------------

Inline LESS::

  {% load less %}

  <style>
    {% inlineless %}
      #header {
        h1 {
          font-size: 26px;
          font-weight: bold;
        }
        p { font-size: 12px;
          a { text-decoration: none;
            &:hover { border-width: 1px }
          }
        }
      }
    {% endinlineless %}
  </style>

renders to::

  <style>
    #header h1 {
      font-size: 26px;
      font-weight: bold;
    }
    #header p {
      font-size: 12px;
    }
    #header p a {
      text-decoration: none;
    }
    #header p a:hover {
      border-width: 1px;
    }
  </style>

External file::

  {% load less %}

  <link rel="stylesheet" href="{{ STATIC_URL}}{% less "path/to/styles.less" %}" />

renders to::

  <link rel="stylesheet" href="/static/COMPILED/path/to/styles.css" />


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

You can run ``compilestatic`` in watch mode (``--watch`` option) when it monitors the changes in your source files and
re-compiles them on the fly. It can be handy if you use tools such as `LiveReload <http://livereload.com/>`_.

You should install `Watchdog <http://pythonhosted.org/watchdog/>`_ to use watch mode.
