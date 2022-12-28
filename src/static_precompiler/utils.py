import json
import os
import posixpath
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Union

import django.conf
import django.core.cache
import django.core.exceptions
from django.utils import encoding

from . import settings


def get_file_encoding() -> str:
    return getattr(django.conf.settings, "FILE_CHARSET", "utf-8")


def normalize_path(posix_path: str) -> str:
    """Convert posix style path to OS-dependent path."""
    if settings.POSIX_COMPATIBLE:
        return posix_path
    return os.path.join(*posix_path.split("/"))


def read_file(path: str) -> str:
    """Return the contents of a file as text."""
    with open(path, encoding=get_file_encoding()) as file_object:
        return file_object.read()


def write_file(content: str, path: str) -> None:
    """Write text content to a file."""

    # Convert to unicode
    content = encoding.force_str(content)

    with open(path, "w+", encoding=get_file_encoding()) as file_object:
        file_object.write(content)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in a string."""
    return " ".join(text.split())


# noinspection PyShadowingBuiltins
def run_command(
    args: List[str], input: Optional[Union[bytes, str]] = None, cwd: Optional[str] = None
) -> Tuple[int, str, str]:

    popen_kwargs: Dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }

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
    assert return_code is not None

    return return_code, encoding.smart_str(output), encoding.smart_str(error)


def compile_static(path: str) -> str:
    from . import registry

    return registry.get_compiler_by_path(path).compile(path)


def compile_static_lazy(path: str) -> str:
    from . import registry

    return registry.get_compiler_by_path(path).compile_lazy(path)


def fix_sourcemap(sourcemap_full_path: str, source_path: str, compiled_full_path: str) -> None:

    sourcemap = json.loads(read_file(sourcemap_full_path))

    # Stylus, unlike SASS, can't add correct relative paths in source map when the compiled file
    # is not in the same dir as the source file. We fix it here.
    sourcemap["sourceRoot"] = "../" * len(source_path.split("/")) + posixpath.dirname(source_path)
    sourcemap["sources"] = [os.path.basename(source) for source in sourcemap["sources"]]
    sourcemap["file"] = posixpath.basename(os.path.basename(compiled_full_path))

    write_file(json.dumps(sourcemap), sourcemap_full_path)
