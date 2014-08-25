from django.template.base import Library
from static_precompiler.compilers import SASS
from static_precompiler.templatetags.compile_static import register_compiler_tags


register = Library()
compiler = SASS()


register_compiler_tags(register, compiler)
