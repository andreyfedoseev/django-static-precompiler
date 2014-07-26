from django.template.base import Library
from static_precompiler.compilers import SASS
from static_precompiler.templatetags.base import BaseInlineNode
from static_precompiler.templatetags.compile_static import compile_tag


register = Library()
compiler = SASS()


class InlineSASSNode(BaseInlineNode):

    compiler = compiler


#noinspection PyUnusedLocal
@register.tag(name="inlinesass")
def do_inlinesass(parser, token):
    nodelist = parser.parse(("endinlinesass",))
    parser.delete_first_token()
    return InlineSASSNode(nodelist)


@register.simple_tag(name="sass")
def sass_tag(source_path):
    return compile_tag(source_path, compiler)
