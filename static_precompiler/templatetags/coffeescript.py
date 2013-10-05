from django.template.base import Library
from static_precompiler.compilers.coffeescript import CoffeeScript
from static_precompiler.templatetags.base import BaseInlineNode


register = Library()
compiler = CoffeeScript()


class InlineCoffeescriptNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlinecoffeescript")
def do_inlinecoffeescript(parser, token):
    nodelist = parser.parse(("endinlinecoffeescript",))
    parser.delete_first_token()
    return InlineCoffeescriptNode(nodelist)


@register.simple_tag
def coffeescript(path):
    return compiler.compile(path)
