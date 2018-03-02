import importlib
import warnings

import django.apps
import django.core.exceptions
from django.utils import six
from typing import *  # noqa

from . import exceptions, settings
from .compilers import BaseCompiler  # noqa

registry = None


def get_compilers():
    # type: () -> Dict[str, BaseCompiler]
    global registry
    if registry is None:
        registry = build_compilers()
    return registry


def build_compilers():
    # type: () -> Dict[str, BaseCompiler]
    # noinspection PyShadowingNames
    compilers = {}
    for compiler_path in settings.COMPILERS:
        compiler_options = {}
        if isinstance(compiler_path, (tuple, list)):
            if len(compiler_path) != 2:
                raise django.core.exceptions.ImproperlyConfigured(
                    'Compiler must be specified in the format ("path.to.CompilerClass", {{compiler options...}}),'
                    ' got {0}'.format(compiler_path)
                )
            compiler_path, compiler_options = compiler_path
            if not isinstance(compiler_options, dict):
                raise django.core.exceptions.ImproperlyConfigured(
                    'Compiler options must be a dict, got {0}'.format(compiler_options)
                )

        try:
            compiler_module, compiler_classname = compiler_path.rsplit('.', 1)
        except ValueError:
            raise django.core.exceptions.ImproperlyConfigured('{0} isn\'t a compiler module'.format(compiler_path))
        try:
            mod = importlib.import_module(compiler_module)
        except ImportError as e:
            raise django.core.exceptions.ImproperlyConfigured(
                'Error importing compiler {0}: "{1}"'.format(compiler_module, e)
            )
        try:
            compiler_class = getattr(mod, compiler_classname)
        except AttributeError:
            raise django.core.exceptions.ImproperlyConfigured(
                'Compiler module "{0}" does not define a "{1}" class'.format(compiler_module, compiler_classname)
            )

        compiler_to_add = compiler_class(**compiler_options)
        compiler = compilers.setdefault(compiler_class.name, compiler_to_add)
        if compiler_to_add != compiler:
            warnings.warn("Both compilers {0} and {1} have the same name.".format(compiler_to_add, compiler))

    return compilers


def get_compiler_by_name(name):
    # type: (str) -> BaseCompiler
    try:
        return get_compilers()[name]
    except KeyError:
        raise exceptions.CompilerNotFound("There is no compiler with name '{0}'.".format(name))


def get_compiler_by_path(path):
    # type: (str) -> BaseCompiler
    for compiler in six.itervalues(get_compilers()):
        if compiler.is_supported(path):
            return compiler

    raise exceptions.UnsupportedFile(
        "The source file '{0}' is not supported by any of available compilers.".format(path)
    )
