=========================
Django Static Precompiler
=========================

Django Static Precompiler provides template tags and filters to compile CoffeeScript, LiveScript, SASS / SCSS, LESS, Stylus, Babel and Handlebars.
It works with both inline code and external files.

.. image:: https://circleci.com/gh/andreyfedoseev/django-static-precompiler.svg?style=shield
    :target: https://circleci.com/gh/andreyfedoseev/django-static-precompiler
    :alt: Build Status

.. image:: https://codecov.io/github/andreyfedoseev/django-static-precompiler/coverage.svg?branch=master
    :target: https://codecov.io/github/andreyfedoseev/django-static-precompiler?branch=master
    :alt: Code Coverage

.. image:: https://codeclimate.com/github/andreyfedoseev/django-static-precompiler/badges/gpa.svg
    :target: https://codeclimate.com/github/andreyfedoseev/django-static-precompiler
    :alt: Code Climate

.. image:: https://readthedocs.org/projects/django-static-precompiler/badge/
    :target: https://django-static-precompiler.readthedocs.io/
    :alt: Documentation

.. image:: https://badges.gitter.im/Join Chat.svg
    :target: https://gitter.im/andreyfedoseev/django-static-precompiler?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
    :alt: Gitter

Documentation
=============

Documentation is available at `http://django-static-precompiler.readthedocs.io <http://django-static-precompiler.readthedocs.io/en/stable/>`_.


Install
=======

.. code-block:: sh

    pip install django-static-precompiler

Use in templates
================

.. code-block:: django

  {% load compile_static %}
  {% load static %}

  <script src="{% static "path/to/script.coffee"|compile %}"></script>
  <link rel="stylesheet" href="{% static "path/to/styles1.less"|compile %}" />
  <link rel="stylesheet" href="{% static "path/to/styles2.scss"|compile %}" />


Use in Python
=============

.. code-block:: python

    >>> from static_precompiler.utils import compile_static
    >>> compile_static("styles.scss")
    "COMPILED/styles.css"


Django compatibility
====================

========================= ==== ==== ==== ==== ==== ====
django-static-precompiler Django
------------------------- -----------------------------
version                   1.11 1.10 1.9  1.8  1.7  1.6
========================= ==== ==== ==== ==== ==== ====
1.6                       \+   \+   \+   \+   \+
1.5                            \+   \+   \+   \+   \+
1.1-1.4                             \+   \+   \+   \+
1.0                                           \+   \+
========================= ==== ==== ==== ==== ==== ====
