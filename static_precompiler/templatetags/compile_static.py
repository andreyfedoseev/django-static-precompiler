from django.utils import six
import warnings

from django.template import Library
from django.templatetags.static import static
from static_precompiler.settings import PREPEND_STATIC_URL, USE_CACHE, CACHE_TIMEOUT
from static_precompiler.utils import compile_static, get_compiler_by_name, get_cache_key, get_hexdigest, get_cache
from static_precompiler.templatetags.base import container_tag


register = Library()


@register.simple_tag(name="compile")
def compile_tag(source_path, compiler=None):
    if compiler:
        compiled = compiler.compile(source_path)
    else:
        compiled = compile_static(source_path)
    if PREPEND_STATIC_URL:
        compiled = static(compiled)
    return compiled


@container_tag(register)
def inlinecompile(nodelist, context, compiler):
    source = nodelist.render(context)

    if isinstance(compiler, six.string_types):
        compiler = get_compiler_by_name(compiler)

    if USE_CACHE:
        cache_key = get_cache_key("{0}.{1}".format(
            compiler.__class__.__name__,
            get_hexdigest(source)
        ))
        cache = get_cache()
        cached = cache.get(cache_key, None)
        if cached is not None:
            return cached
        output = compiler.compile_source(source)
        cache.set(cache_key, output, CACHE_TIMEOUT)
        return output

    return compiler.compile_source(source)


def _warn(old, new):
    warnings.warn(
        "{%% %s %%} tag has been deprecated, use {%% %s %%} "
        "from `compile_static` template tag library instead." % (old, new),
        DeprecationWarning,
    )


def register_compiler_tags(register, compiler):
    @register.simple_tag(name=compiler.name)
    def tag(source_path):
        _warn(compiler.name, 'compile')
        return compile_tag(source_path, compiler)

    @container_tag(register, name="inline" + compiler.name)
    def inline_tag(nodelist, context):
        _warn('inline%s' % compiler.name, 'inlinecompile "%s"' % compiler.name)
        return inlinecompile(nodelist, context, compiler)
