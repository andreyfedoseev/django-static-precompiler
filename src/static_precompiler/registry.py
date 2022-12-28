import importlib
import warnings
from typing import Dict, Optional

import django.apps
import django.core.exceptions

from . import exceptions, settings
from .compilers import BaseCompiler

registry: Optional[Dict[str, BaseCompiler]] = None


def get_compilers() -> Dict[str, BaseCompiler]:
    global registry
    if registry is None:
        registry = build_compilers()
    return registry


def build_compilers() -> Dict[str, BaseCompiler]:
    # noinspection PyShadowingNames
    compilers: Dict[str, BaseCompiler] = {}
    for compiler_path in settings.COMPILERS:
        compiler_options = {}
        if isinstance(compiler_path, (tuple, list)):
            if len(compiler_path) != 2:
                raise django.core.exceptions.ImproperlyConfigured(
                    'Compiler must be specified in the format ("path.to.CompilerClass", {{compiler options...}}),'
                    " got {0}".format(compiler_path)
                )
            compiler_path, compiler_options = compiler_path
            if not isinstance(compiler_options, dict):
                raise django.core.exceptions.ImproperlyConfigured(
                    f"Compiler options must be a dict, got {compiler_options}"
                )

        try:
            compiler_module, compiler_classname = compiler_path.rsplit(".", 1)
        except ValueError:
            raise django.core.exceptions.ImproperlyConfigured(f"{compiler_path} isn't a compiler module") from None
        try:
            mod = importlib.import_module(compiler_module)
        except ImportError as e:
            raise django.core.exceptions.ImproperlyConfigured(
                f'Error importing compiler {compiler_module}: "{e}"'
            ) from None
        try:
            compiler_class = getattr(mod, compiler_classname)
        except AttributeError:
            raise django.core.exceptions.ImproperlyConfigured(
                f'Compiler module "{compiler_module}" does not define a "{compiler_classname}" class'
            ) from None

        compiler_to_add = compiler_class(**compiler_options)
        compiler = compilers.setdefault(compiler_class.name, compiler_to_add)
        if compiler_to_add != compiler:
            warnings.warn(f"Both compilers {compiler_to_add} and {compiler} have the same name.")

    return compilers


def get_compiler_by_name(name: str) -> BaseCompiler:
    try:
        return get_compilers()[name]
    except KeyError:
        raise exceptions.CompilerNotFound(f"There is no compiler with name '{name}'.") from None


def get_compiler_by_path(path: str) -> BaseCompiler:
    for compiler in get_compilers().values():
        if compiler.is_supported(path):
            return compiler

    raise exceptions.UnsupportedFile(f"The source file '{path}' is not supported by any of available compilers.")
