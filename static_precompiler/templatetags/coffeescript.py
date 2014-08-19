from django.template.base import Library
from static_precompiler.compilers import CoffeeScript
from static_precompiler.templatetags.compile_static import register_compiler_tags


register = Library()
compiler = CoffeeScript()


register_compiler_tags(register, compiler)
