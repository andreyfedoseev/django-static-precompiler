from django.template.base import Library
from django.templatetags.static import static
from static_precompiler.compilers import SASS
from static_precompiler.templatetags.base import BaseInlineNode


register = Library()
compiler = SASS()


class InlineSASSNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlinesass")
def do_inlinecoffeescript(parser, token):
    nodelist = parser.parse(("endinlinesass",))
    parser.delete_first_token()
    return InlineSASSNode(nodelist)


@register.simple_tag
def sass(path):
    return compiler.compile(str(path))


@register.simple_tag
def static_sass(path):
    return static(sass(path))
