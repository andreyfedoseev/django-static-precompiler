from django.template import Library
from django.templatetags.static import static
from static_precompiler.settings import PREPEND_STATIC_URL
from static_precompiler.utils import compile_static


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
