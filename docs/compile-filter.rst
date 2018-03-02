***************************
``compile`` template filter
***************************

``compile`` is a template filter that allows to compile any source file supported by compilers configured with
``STATIC_PRECOMPILER_COMPILERS`` settings.

Example
=======

.. code-block:: html+django

  {% load compile_static %}
  {% load static %}

  <script src="{% static "path/to/script.coffee"|compile %}"></script>
  <link rel="stylesheet" href="{% static "path/to/styles1.less"|compile %}" />
  <link rel="stylesheet" href="{% static "path/to/styles2.scss"|compile %}" />

renders to:

.. code-block:: html

  <script src="/static/COMPILED/path/to/script.js"></script>
  <link rel="stylesheet" href="/static/COMPILED/path/to/styles1.css" />
  <link rel="stylesheet" href="/static/COMPILED/path/to/styles2.css" />

