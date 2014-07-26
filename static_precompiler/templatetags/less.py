from django.template.base import Library
from static_precompiler.compilers import LESS
from static_precompiler.templatetags.base import BaseInlineNode
from static_precompiler.templatetags.compile_static import compile_tag


register = Library()
compiler = LESS()


class InlineLESSNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlineless")
def do_inlineless(parser, token):
    nodelist = parser.parse(("endinlineless",))
    parser.delete_first_token()
    return InlineLESSNode(nodelist)


@register.simple_tag(name="less")
def less_tag(source_path):
    return compile_tag(source_path, compiler)

