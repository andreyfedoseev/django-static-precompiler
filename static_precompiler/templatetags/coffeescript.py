from django.template.base import Library
from static_precompiler.compilers import CoffeeScript
from static_precompiler.templatetags.base import BaseInlineNode
from static_precompiler.templatetags.compile_static import compile_tag


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


@register.simple_tag(name="coffeescript")
def coffeescript_tag(source_path):
    return compile_tag(source_path, compiler)
