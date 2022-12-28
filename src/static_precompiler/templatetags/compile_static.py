import warnings
from typing import Any, Optional, Union

import django.template
import django.templatetags.static

from static_precompiler.compilers import BaseCompiler

from .. import caching, registry, settings, utils

register = django.template.Library()


@register.filter(name="compile")
def compile_filter(source_path: str) -> str:
    compiled = utils.compile_static(source_path)
    if settings.PREPEND_STATIC_URL:
        compiled = django.templatetags.static.static(compiled)
    return compiled


@register.simple_tag(name="compile")
def compile_tag(source_path: str, compiler: Optional[BaseCompiler] = None) -> str:
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


class InlineCompileNode(django.template.Node):
    def __init__(self, nodelist: Any, compiler: str):
        self.nodelist = nodelist
        self.compiler = compiler

    def render(self, context: Any) -> str:
        source = self.nodelist.render(context)

        compiler: Union[str, BaseCompiler]

        if self.compiler[0] == self.compiler[-1] and self.compiler[0] in ('"', "'"):
            compiler = self.compiler[1:-1]
        else:
            compiler = django.template.Variable(self.compiler).resolve(context)

        if isinstance(compiler, str):
            compiler = registry.get_compiler_by_name(compiler)

        if settings.USE_CACHE:
            cache_key = caching.get_cache_key(f"{compiler.__class__.__name__}.{caching.get_hexdigest(source)}")
            cache = caching.get_cache()
            cached: Optional[str] = cache.get(cache_key, None)
            if cached is not None:
                return cached
            output = compiler.compile_source(source)
            cache.set(cache_key, output, settings.CACHE_TIMEOUT)
            return output

        return compiler.compile_source(source)


@register.tag
def inlinecompile(parser: Any, token: Any) -> Any:
    bits = token.split_contents()
    tag_name = bits[0]
    try:
        (compiler,) = bits[1:]
    except ValueError:
        raise django.template.TemplateSyntaxError(f"{tag_name!r} tag requires exactly one argument.") from None
    if compiler.startswith("compiler="):
        compiler = compiler[len("compiler=") :]
    nodelist = parser.parse(("end" + tag_name,))
    parser.delete_first_token()
    return InlineCompileNode(nodelist, compiler)
