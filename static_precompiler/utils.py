import json
import os
import posixpath
import subprocess

import django.conf
import django.core.cache
import django.core.exceptions
from django.utils import encoding, six

from . import settings


def normalize_path(posix_path):
    """ Convert posix style path to OS-dependent path.
    """
    if settings.POSIX_COMPATIBLE:
        return posix_path
    return os.path.join(*posix_path.split("/"))


def read_file(path):
    """ Return the contents of a file as unicode. """
    if six.PY2:
        with open(path) as file_object:
            return file_object.read().decode(django.conf.settings.FILE_CHARSET)
    else:
        with open(path, encoding=django.conf.settings.FILE_CHARSET) as file_object:
            return file_object.read()


def write_file(content, path):
    """ Write unicode content to a file. """

    # Convert to unicode
    content = encoding.force_text(content)

    if six.PY2:
        with open(path, "w+") as file_object:
            file_object.write(content.encode(django.conf.settings.FILE_CHARSET))
    else:
        with open(path, "w+", encoding=django.conf.settings.FILE_CHARSET) as file_object:
            file_object.write(content)


def fix_line_breaks(text):
    """ Convert Win line breaks to Unix
    """
    return text.replace("\r\n", "\n")


# noinspection PyShadowingBuiltins
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
        input = encoding.smart_bytes(input)

    output, error = p.communicate(input)
    return_code = p.poll()

    return return_code, encoding.smart_str(output), encoding.smart_str(error)


def compile_static(path):
    # type: (str) -> str
    from . import registry
    return registry.get_compiler_by_path(path).compile(path)


def compile_static_lazy(path):
    from . import registry
    return registry.get_compiler_by_path(path).compile_lazy(path)


def fix_sourcemap(sourcemap_full_path, source_path, compiled_full_path):

    sourcemap = json.loads(read_file(sourcemap_full_path))

    # Stylus, unlike SASS, can't add correct relative paths in source map when the compiled file
    # is not in the same dir as the source file. We fix it here.
    sourcemap["sourceRoot"] = "../" * len(source_path.split("/")) + posixpath.dirname(source_path)
    sourcemap["sources"] = [os.path.basename(source) for source in sourcemap["sources"]]
    sourcemap["file"] = posixpath.basename(os.path.basename(compiled_full_path))

    write_file(json.dumps(sourcemap), sourcemap_full_path)
