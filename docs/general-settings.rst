****************
General settings
****************

``STATIC_PRECOMPILER_COMPILERS``
  List of enabled compilers. You can modify it to enable your custom compilers. Default:

  .. code-block:: python

    STATIC_PRECOMPILER_COMPILERS = (
        'static_precompiler.compilers.CoffeeScript',
        'static_precompiler.compilers.Babel',
        'static_precompiler.compilers.Handlebars',
        'static_precompiler.compilers.SASS',
        'static_precompiler.compilers.SCSS',
        'static_precompiler.compilers.LESS',
        'static_precompiler.compilers.Stylus',
    )

  You can specify compiler options using the following format:

  .. code-block:: python

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
  Add ``STATIC_URL`` to the output of template tags and filters. Default: ``False``.

``STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE``
  Disable automatic compilation from template tags or ``compile_static`` utility function. Files are compiled
  only with ``compilestatic`` command (see below). Default: ``False``.

``STATIC_PRECOMPILER_FINDER_LIST_FILES``
  Whether or not ``static_precompiler.finders.StaticPrecompilerFinder`` will list compiled files when ``collectstatic``
  command is executed. Set to ``True`` if you want compiled files to be found by ``collectstatic``. Default: ``False``.

