from django.core.cache import get_cache as base_get_cache, cache as default_cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str, smart_bytes
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module
from hashlib import md5
from static_precompiler.exceptions import UnsupportedFile, CompilerNotFound
from static_precompiler.settings import MTIME_DELAY, POSIX_COMPATIBLE, COMPILERS, \
    STATIC_URL, CACHE_NAME
from django.utils import six
from warnings import warn
import os
import re
import socket
import subprocess


if six.PY2:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin
else:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin


def normalize_path(posix_path):
    """ Convert posix style path to OS-dependent path.
    """
    if POSIX_COMPATIBLE:
        return posix_path
    return os.path.join(*posix_path.split("/"))


def fix_line_breaks(text):
    """ Convert Win line breaks to Unix
    """
    return text.replace("\r\n", "\n")


def get_hexdigest(plaintext, length=None):
    digest = md5(smart_bytes(plaintext)).hexdigest()
    if length:
        return digest[:length]
    return digest


def get_cache():
    if CACHE_NAME:
        return base_get_cache(CACHE_NAME)
    return default_cache


def get_cache_key(key):
    return "static_precompiler.{0}.{1}".format(socket.gethostname(), key)


def get_mtime_cachekey(filename):
    return get_cache_key("mtime.{0}".format(get_hexdigest(filename)))


def get_mtime(filename):
    if MTIME_DELAY:
        key = get_mtime_cachekey(filename)
        cache = get_cache()
        mtime = cache.get(key)
        if mtime is None:
            mtime = os.path.getmtime(filename)
            cache.set(key, mtime, MTIME_DELAY)
        return mtime
    return os.path.getmtime(filename)


#noinspection PyShadowingBuiltins
def run_command(args, input=None, cwd=None):

    popen_kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if cwd is not None:
        popen_kwargs["cwd"] = cwd

    if input is not None:
        popen_kwargs["stdin"] = subprocess.PIPE

    if os.name == "nt":
        popen_kwargs["shell"] = True

    p = subprocess.Popen(args, **popen_kwargs)

    if input:
        input = smart_bytes(input)

    output, error = p.communicate(input)

    return smart_str(output), smart_str(error)


class URLConverter(object):

    URL_PATTERN = re.compile(r"url\(([^\)]+)\)")

    @staticmethod
    def convert_url(url, source_dir):
        assert source_dir[-1] == "/"
        url = url.strip(' \'"')
        if url.startswith(('http://', 'https://', '/', 'data:')):
            return url
        return urljoin(STATIC_URL, urljoin(source_dir, url))

    def convert(self, content, path):
        source_dir = os.path.dirname(path)
        if not source_dir.endswith("/"):
            source_dir += "/"
        return self.URL_PATTERN.sub(
            lambda matchobj: "url('{0}')".format(
                self.convert_url(matchobj.group(1), source_dir)
            ),
            content
        )


url_converter = URLConverter()


def convert_urls(content, path):
    return url_converter.convert(content, path)


def _build_compilers():
    # noinspection PyShadowingNames
    compilers = {}
    for compiler_path in COMPILERS:
        compiler_options = {}
        if isinstance(compiler_path, (tuple, list)):
            if len(compiler_path) != 2:
                raise ImproperlyConfigured(
                    'Compiler must be specified in the format ("path.to.CompilerClass", {{compiler options...}}),'
                    ' got {0}'.format(compiler_path)
                )
            compiler_path, compiler_options = compiler_path
            if not isinstance(compiler_options, dict):
                raise ImproperlyConfigured('Compiler options must be a dict, got {0}'.format(compiler_options))

        try:
            compiler_module, compiler_classname = compiler_path.rsplit('.', 1)
        except ValueError:
            raise ImproperlyConfigured('{0} isn\'t a compiler module'.format(compiler_path))
        try:
            mod = import_module(compiler_module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing compiler {0}: "{1}"'.format(compiler_module, e))
        try:
            compiler_class = getattr(mod, compiler_classname)
        except AttributeError:
            raise ImproperlyConfigured('Compiler module "{0}" does not define a "{1}" class'.format(compiler_module, compiler_classname))

        compiler_to_add = compiler_class(**compiler_options)
        compiler = compilers.setdefault(compiler_class.name, compiler_to_add)
        if compiler_to_add != compiler:
            warn("Both compilers {0} and {1} have the same name.".format(compiler_to_add, compiler))

    return compilers


compilers = None


def get_compilers():
    global compilers
    if compilers is None:
        compilers = _build_compilers()
    return compilers


def get_compiler_by_name(name):
    try:
        return get_compilers()[name]
    except KeyError:
        raise CompilerNotFound("There is no compiler with name '{0}'.".format(name))


def get_compiler_by_path(path):
    for compiler in six.itervalues(get_compilers()):
        if compiler.is_supported(path):
            return compiler

    raise UnsupportedFile("The source file '{0}' is not supported by any of available compilers.".format(path))


def compile_static(path):

    return get_compiler_by_path(path).compile(path)


def compile_static_lazy(path):

    return get_compiler_by_path(path).compile_lazy(path)
