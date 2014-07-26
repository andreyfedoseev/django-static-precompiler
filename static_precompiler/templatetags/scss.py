from django.template.base import Library
from static_precompiler.compilers import SCSS
from static_precompiler.templatetags.base import BaseInlineNode
from static_precompiler.templatetags.compile_static import compile_tag


register = Library()
compiler = SCSS()


class InlineSCSSNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlinescss")
def do_inlinescss(parser, token):
    nodelist = parser.parse(("endinlinescss",))
    parser.delete_first_token()
    return InlineSCSSNode(nodelist)


@register.simple_tag(name="scss")
def scss_tag(source_path):
    return compile_tag(source_path, compiler)
