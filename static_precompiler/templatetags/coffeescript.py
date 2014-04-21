from django.template.base import Library
from static_precompiler.compilers import CoffeeScript
from static_precompiler.templatetags.base import BaseInlineNode
from static_precompiler.utils import prepend_static_url


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
    return prepend_static_url(compiler.compile(str(path)))

