from django.template.base import Library
from static_precompiler.compilers import LESS
from static_precompiler.templatetags.compile_static import register_compiler_tags


register = Library()
compiler = LESS()


register_compiler_tags(register, compiler)
