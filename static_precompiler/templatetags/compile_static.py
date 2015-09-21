import warnings

import django.template
import django.templatetags.static
from django.utils import six

from static_precompiler import settings, utils

from . import base

register = django.template.Library()


@register.filter(name="compile")
def compile_filter(source_path):
    compiled = utils.compile_static(source_path)
    if settings.PREPEND_STATIC_URL:
        compiled = django.templatetags.static.static(compiled)
    return compiled


@register.simple_tag(name="compile")
def compile_tag(source_path, compiler=None):
    warnings.warn(
        "{% compile %} tag has been deprecated, use `compile` filter from `compile_static` template tag library "
        "instead.",
        DeprecationWarning,
    )
    if compiler:
        compiled = compiler.compile(source_path)
    else:
        compiled = utils.compile_static(source_path)
    if settings.PREPEND_STATIC_URL:
        compiled = django.templatetags.static.static(compiled)
    return compiled


@base.container_tag(register)
def inlinecompile(nodelist, context, compiler):
    source = nodelist.render(context)

    if isinstance(compiler, six.string_types):
        compiler = utils.get_compiler_by_name(compiler)

    if settings.USE_CACHE:
        cache_key = utils.get_cache_key("{0}.{1}".format(
            compiler.__class__.__name__,
            utils.get_hexdigest(source)
        ))
        cache = utils.get_cache()
        cached = cache.get(cache_key, None)
        if cached is not None:
            return cached
        output = compiler.compile_source(source)
        cache.set(cache_key, output, settings.CACHE_TIMEOUT)
        return output

    return compiler.compile_source(source)
