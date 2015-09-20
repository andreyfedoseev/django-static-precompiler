import inspect

import django.template.base


def container_tag(register, name=None):
    def dec(func):
        params, varargs, varkw, defaults = inspect.getargspec(func)
        params = params[1:]
        tag_name = name or func.__name__

        class InlineCompileNode(django.template.base.TagHelperNode):

            def __init__(self, nodelist, *args):
                super(InlineCompileNode, self).__init__(*args)
                self.nodelist = nodelist

            def render(self, context):
                args, kwargs = self.get_resolved_arguments(context)
                return func(self.nodelist, *args, **kwargs)

        def compile_func(parser, token):
            takes_context = True
            bits = token.split_contents()[1:]
            args, kwargs = django.template.base.parse_bits(parser, bits, params, varargs, varkw,
                                                           defaults, takes_context, tag_name)
            nodelist = parser.parse(('end' + tag_name,))
            parser.delete_first_token()
            return InlineCompileNode(nodelist, takes_context, args, kwargs)

        register.tag(tag_name, compile_func)
        return func

    return dec
