from django.template.base import Library
from static_precompiler.compilers import SCSS
from static_precompiler.templatetags.base import BaseInlineNode


register = Library()
compiler = SCSS()


class InlineSCSSNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlinescss")
def do_inlinecoffeescript(parser, token):
    nodelist = parser.parse(("endinlinescss",))
    parser.delete_first_token()
    return InlineSCSSNode(nodelist)


@register.simple_tag
def scss(path):
    return compiler.compile(str(path))
