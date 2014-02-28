from django.template.base import Library
from static_precompiler.compilers import LESS
from static_precompiler.templatetags.base import BaseInlineNode


register = Library()
compiler = LESS()


class InlineLESSNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlineless")
def do_inlinecoffeescript(parser, token):
    nodelist = parser.parse(("endinlineless",))
    parser.delete_first_token()
    return InlineLESSNode(nodelist)


@register.simple_tag
def less(path):
    return compiler.compile(str(path))
