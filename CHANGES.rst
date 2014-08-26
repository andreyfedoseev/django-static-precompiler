=======
Changes
=======

0.8
===

- Add ``{% inlinecompile %}`` template tag
- **These compiler specific template tags are DEPRECATED:**

  * ``{% coffeescript %}``
  * ``{% inlinecoffeescript %}``
  * ``{% sass %}``
  * ``{% inlinesass %}``
  * ``{% scss %}``
  * ``{% inlinescss %}``
  * ``{% less %}``
  * ``{% inlineless %}``

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
