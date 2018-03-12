**************************
Compiler specific settings
**************************

CoffeeScript
============

``executable``
  Path to CoffeeScript compiler executable. Default: ``"coffee"``.

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.CoffeeScript', {
            "executable": "/usr/bin/coffee",
            "sourcemap_enabled": True,
        }),
    )


Babel
=====

``executable``
  Path to Babel compiler executable. Default: ``"babel"``.

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

``plugins``
  Babel `plugins <http://babeljs.io/docs/plugins/>`_ command line option. Default: ``None`` (uses Babel's default option).

``presets``
  Babel `presets <http://babeljs.io/docs/plugins/#presets>`_ command line option. Default: ``None`` (uses Babel's default option).

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.Babel', {
            "executable": "/usr/bin/babel",
            "sourcemap_enabled": True,
            "plugins": "transform-react-jsx",
            "presets": "es2015,react",
        }),
    )


LiveScript
==========

``executable``
  Path to LiveScript compiler executable. Default: ``"lsc"``.

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.LiveScript', {
            "executable": "/usr/bin/lsc",
            "sourcemap_enabled": True,
        }),
    )


Handlebars
==========

``executable``
  Path to Handlebars compiler executable. Default: ``"handlebars"``.

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

``known_helpers``
  List of known helpers (``-k`` compiler option). Default: ``None``.

``namespace``
  Template namespace (``-n`` compiler option). Default: ``None``.

``simple``
  Output template function only (``-s`` compiler option). Default: ``False``.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.Handlebars', {
            "executable": "/usr/bin/handlebars",
            "sourcemap_enabled": True,
            "simple": True,
        }),
    )


SASS / SCSS
===========

``executable``
  Path to SASS compiler executable. Default: "sass".

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

``compass_enabled``
  Boolean. Whether to use compass or not. Compass must be installed in your system.
  Run ``sass --compass`` and if no error is shown it means that compass is installed.

``load_paths``
  List of additional directories to look imported files (``--load-path`` command line option). Default: ``None``.

``precision``
  How many digits of precision to use when outputting decimal numbers. Default: ``None``.
  Set this to 8 or more if you compile Bootstrap.

``output_style``
  Output style. Default: ``None``.
  Can be nested, compact, compressed, or expanded.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.SCSS', {
            "executable": "/usr/bin/sass",
            "sourcemap_enabled": True,
            "compass_enabled": True,
            "load_paths": ["/path"],
            "precision": 8,
            "output_style": "compressed",
        }),
    )


Libsass
=======

`Libsass <https://github.com/sass/libsass>`_ is a C/C++ implementation of SASS.
``django-static-precompiler`` uses `libsass-python <http://hongminhee.org/libsass-python/>`_ bindings for ``libsass``

To use SASS / SCSS compiler based on ``libsass`` install ``django-static-precompiler`` with ``libsass`` flavor::

    pip install django-static-precompiler[libsass]


.. note:: Libsass compiler is disabled by default. See how to enable it in the example below.

Options:

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

``load_paths``
  List of additional paths to find imports. Default: ``None``.

``precision``
  How many digits of precision to use when outputting decimal numbers. Default: ``None``.
  Set this to 8 or more if you compile Bootstrap.

``output_style``
  Output style. Default: ``None``.
  Can be nested, compact, compressed, or expanded.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.libsass.SCSS', {
            "sourcemap_enabled": True,
            "load_paths": ["/path"],
            "precision": 8,
        }),
        ('static_precompiler.compilers.libsass.SASS', {
            "sourcemap_enabled": True,
            "load_paths": ["/path"],
            "precision": 8,
            "output_style": "compressed",
        }),
    )

.. note:: Libsass compiler doesn't support Compass extension, but you can replace it with `compass-mixins <https://github.com/Igosuki/compass-mixins>`_.


LESS
====

``executable``
  Path to LESS compiler executable. Default: ``"lessc"``.

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

``include_path``
  List of additional directories to look for imported files (``--include-path`` command line option). Default: ``None``.

``clean_css``
  Boolean. Set to ``True`` to use the `clean-css <https://github.com/less/less-plugin-clean-css>`_ plugin to minify the output. Default ``False``.

``global_vars``
  Dictionary of global variables (``--global-var`` command line option). Default: ``None``.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.LESS', {
            "executable": "/usr/bin/lessc",
            "sourcemap_enabled": True,
            "global_vars": {"link-color": "red"},
        }),
    )


Stylus
======

``executable``
  Path to Stylus compiler executable. Default: ``"stylus"``.

``sourcemap_enabled``
  Boolean. Set to ``True`` to enable source maps. Default: ``False``.

Example:

.. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        ('static_precompiler.compilers.Stylus', {"executable": "/usr/bin/stylus", "sourcemap_enabled": True),
    )

