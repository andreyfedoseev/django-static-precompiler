=======
Changes
=======

1.4
===

- Fix the ``run_command`` utility function to rely on process return code rather than stderr to determine if compilation
  has finished successfully. WARNING! Changes in ``run_command`` are backward incompatible. If you use this function in
  your custom compiler you should update your code.


1.3.1
=====

- Add support for ``--presets`` option in Babel compiler. See babel-cli `options <https://babeljs.io/docs/usage/options/>` for more information.

1.3
===

- Fix Stylus compiler to actually enable support for detecting changes in imported files
- Add ``precision`` option to SASS / SCSS / LibSass compilers. Set it to 8 or more if you compile Bootstrap.
- Add ``output_style`` option to SASS / SCSS / LibSass compilers.
- Enable verbose output for ``compilestatic`` management command

1.2
===

- Add LiveScript compiler
- Add support for ``--global-var`` option in LESS compiler
- Add SCSS / SASS compiler based on Libsass


1.1
===

- Add source maps support for SASS/SCSS
- Add source maps support for LESS
- Add source maps support for CoffeeScript
- Add source maps support for Stylus
- Add source maps support for Babel
- Add `Handlebars <http://handlebarsjs.com/>`_ compiler
- Add support for Django 1.9
- Add ``plugins`` parameter to Babel compiler
- Add ``load_paths`` parameter to SASS/SCSS compilers


1.0.1
=====

- Add ``modules`` parameter to Babel compiler
- Allow to install Watchdog with ``pip install django-static-precompiler[watch]``

1.0
===

- Add ``compile`` template filter
- Deprecate ``{% compile %}`` template tag
- **The following compiler specific template tags are REMOVED:**

  * ``{% coffeescript %}``
  * ``{% inlinecoffeescript %}``
  * ``{% sass %}``
  * ``{% inlinesass %}``
  * ``{% scss %}``
  * ``{% inlinescss %}``
  * ``{% less %}``
  * ``{% inlineless %}``
- Add `Stylus <http://learnboost.github.io/stylus/>`_ compiler

0.9
===

- Compiler options are specified with ``STATIC_PRECOMPILER_COMPILERS`` setting.
- **The following settings are DEPRECATED:**

  * ``COFFEESCRIPT_EXECUTABLE``
  * ``SCSS_EXECUTABLE``
  * ``SCSS_USE_COMPASS``
  * ``LESS_EXECUTABLE``
- ``-C`` (``--no-cache``) flag is removed from SASS/SCSS compilers
- Add ``STATIC_PRECOMPILER_LIST_FILES`` setting
- Add `Babel <https://babeljs.io>`_ compiler

0.8
===

- Add ``{% inlinecompile %}`` template tag
- **The following compiler specific template tags are DEPRECATED:**

  * ``{% coffeescript %}``
  * ``{% inlinecoffeescript %}``
  * ``{% sass %}``
  * ``{% inlinesass %}``
  * ``{% scss %}``
  * ``{% inlinescss %}``
  * ``{% less %}``
  * ``{% inlineless %}``
- Use Django 1.7 migrations
- BUGFIX: fix sass imports from scss and vice versa
- BUGFIX: make sure that ``compilestatic`` works if ``watchdog`` isn't installed.
- BUGFIX: fix compilation error when dependency file was removed or renamed

0.7
===

- Add ``compilestatic`` management command (replaces ``static_precompiler_watch``)
- Add ``STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE`` to settings
- Add ``STATIC_PRECOMPILER_CACHE_NAME`` to settings
- Bugfixes

0.6
===

- Add ``STATIC_PRECOMPILER_PREPEND_STATIC_URL`` to settings
- Add ``{% compile %}`` template tag

0.5.3
=====

- Update the parsing of ``@import`` statements. Fix the bug with URLs containing commas.

0.5.2
=====

- ``static_precompiler_watch``: watch for changes in all directories handled by static finders, not only ``STATIC_ROOT``
- ``static_precompiler_watch``: add ``--no-initial-scan`` option

0.5.1
=====

- Fix SCSS compilation error when importing Compass styles

0.5
===

- Add Python 3 support

0.4
===

- Add ``compile_static`` and ``compile_static_lazy`` utility functions.

0.3
===

- Bug fixes
- Add Windows compatibility


0.2
===

- Reduce the max length of varchar fields in Dependency model to meet MySQL limitations
- static_precompiler_watch: don't fall with exception on compilation errors or if
  source file is not found

0.1
===

- Initial release
