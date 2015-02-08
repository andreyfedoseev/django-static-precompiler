from django.template.base import Library
from static_precompiler.compilers import ES6Script
from static_precompiler.templatetags.compile_static import register_compiler_tags


register = Library()
compiler = ES6Script()


register_compiler_tags(register, compiler)
