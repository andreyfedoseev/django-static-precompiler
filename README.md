## Django Static Precompiler

Django Static Precompiler provides template tags and filters to compile
CoffeeScript, LiveScript, SASS / SCSS, LESS, Stylus, Babel and
Handlebars. It works with both inline code and external files.

[![Build Status](https://github.com/andreyfedoseev/django-static-precompiler/workflows/CI/badge.svg)](https://github.com/andreyfedoseev/django-static-precompiler/actions?query=workflow%3ACI)
[![Documentation](https://readthedocs.org/projects/django-static-precompiler/badge/)](https://django-static-precompiler.readthedocs.io/)

### Documentation

Documentation is available at
<https://django-static-precompiler.readthedocs.io>.

### Install

```sh
pip install django-static-precompiler
```

### Use in templates

```html
{% load compile_static %}
{% load static %}

<script src="{% static "path/to/script.coffee"|compile %}"></script>
<link rel="stylesheet" href="{% static "path/to/styles1.less"|compile %}" />
<link rel="stylesheet" href="{% static "path/to/styles2.scss"|compile %}" />
```

### Use in Python

```python
>>> from static_precompiler.utils import compile_static
>>> compile_static("styles.scss")
"COMPILED/styles.css"
```

### Python & Django compatibility

| django-static-precompiler | Python | Django     |
|---------------------------|--------|------------|
| 2.2+                      | 3.6+   | 2.0 - 4.1  |
| 2.1                       | 3.6+   | 2.0 - 4.0  |
| 2.0                       | 3.4+   | 1.9 - 3.2  |
| 1.7-1.8                   | 2.7+   | 1.7 - 2.2  |
| 1.6                       | 2.7+   | 1.7 - 1.11 |
| 1.5                       | 2.7+   | 1.6 - 1.10 |
| 1.1-1.4                   | 2.7+   | 1.6 - 1.9  |
| 1.0                       | 2.7+   | 1.6 - 1.7  |
