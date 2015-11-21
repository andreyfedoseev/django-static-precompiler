import inspect

try:
    # Django>=1.9
    from django.template import library
except ImportError:
    # Django<1.9
    from django.template import base as library


def container_tag(register, name=None):

    def dec(func):
        params, varargs, varkw, defaults = inspect.getargspec(func)
        params = params[1:]
        tag_name = name or func.__name__

        class InlineCompileNode(library.TagHelperNode):
            def __init__(self, nodelist, *args):
                super(InlineCompileNode, self).__init__(*args)
                self.nodelist = nodelist

            def render(self, context):
                args, kwargs = self.get_resolved_arguments(context)
                return func(self.nodelist, *args, **kwargs)

        def compile_func(parser, token):
            takes_context = True
            bits = token.split_contents()[1:]
            args, kwargs = library.parse_bits(parser, bits, params, varargs, varkw,
                                              defaults, takes_context, tag_name)
            nodelist = parser.parse(('end' + tag_name,))
            parser.delete_first_token()
            try:
                # Django<1.9
                return InlineCompileNode(nodelist, takes_context, args, kwargs)
            except TypeError:
                # Django>=1.9
                return InlineCompileNode(nodelist, func, takes_context, args, kwargs)

        register.tag(tag_name, compile_func)
        return func

    return dec
