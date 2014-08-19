from inspect import getargspec

from django.template import Node
from django.template.base import parse_bits, TagHelperNode

from static_precompiler.settings import USE_CACHE, CACHE_TIMEOUT
from static_precompiler.utils import get_cache_key, get_hexdigest, get_cache


class BaseInlineNode(Node):

    compiler = None

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        source = self.nodelist.render(context)

        if USE_CACHE:
            cache_key = get_cache_key("{0}.{1}".format(
                self.__class__.__name__,
                get_hexdigest(source)
            ))
            cache = get_cache()
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached
            output = self.compiler.compile_source(source)
            cache.set(cache_key, output, CACHE_TIMEOUT)
            return output

        return self.compiler.compile_source(source)


def container_tag(register, name=None):
    def dec(func):
        params, varargs, varkw, defaults = getargspec(func)
        params = params[1:]
        tag_name = name or func.__name__

        class InlineCompileNode(TagHelperNode):

            def __init__(self, nodelist, *args):
                super(InlineCompileNode, self).__init__(*args)
                self.nodelist = nodelist

            def render(self, context):
                args, kwargs = self.get_resolved_arguments(context)
                return func(self.nodelist, *args, **kwargs)

        def compile_func(parser, token):
            takes_context = True
            bits = token.split_contents()[1:]
            args, kwargs = parse_bits(parser, bits, params, varargs, varkw,
                                      defaults, takes_context, tag_name)
            nodelist = parser.parse(('end' + tag_name,))
            parser.delete_first_token()
            return InlineCompileNode(nodelist, takes_context, args, kwargs)

        register.tag(tag_name, compile_func)
        return func

    return dec
