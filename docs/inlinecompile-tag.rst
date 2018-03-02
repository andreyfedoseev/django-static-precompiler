***********************
{% inlinecompile %} tag
***********************

Compiles everything between ``{% inlinecompile %}`` and ``{% endinlinecompile %}`` with compiler specified by name.
Compiler must be specified in ``STATIC_PRECOMPILER_COMPILERS`` setting. Names for default compilers are:

* ``coffeescript``
* ``babel``
* ``less``
* ``sass``
* ``scss``
* ``stylus``

Example
=======

.. code-block:: html+django

  {% load compile_static %}

  <script type="text/javascript">
    {% inlinecompile "coffeescript" %}
      console.log "Hello, World!"
    {% endinlinecompile %}
  </script>

renders to:

.. code-block:: html

  <script type="text/javascript">
    (function() {
      console.log("Hello, World!");
    }).call(this);
  </script>

