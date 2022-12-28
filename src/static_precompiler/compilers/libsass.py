import os
import re
from typing import Any, Dict, Optional

import sass  # type: ignore
from django.utils import encoding

from .. import exceptions, url_converter, utils
from ..types import StrCollection
from . import dart_sass

__all__ = (
    "SCSS",
    "SASS",
)


class SCSS(dart_sass.SCSS):

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*;", re.DOTALL)
    indented = False
    is_compass_enabled = False

    def __init__(
        self,
        sourcemap_enabled: bool = False,
        load_paths: Optional[StrCollection] = None,
        precision: Optional[int] = None,
        output_style: Optional[str] = None,
    ):
        self.is_sourcemap_enabled = sourcemap_enabled
        self.precision = precision
        self.output_style = output_style
        self.load_paths: StrCollection = load_paths or []
        super(dart_sass.SCSS, self).__init__()

    def compile_file(self, source_path: str) -> str:
        full_source_path = self.get_full_source_path(source_path)
        full_output_path = self.get_full_output_path(source_path)

        full_output_dirname = os.path.dirname(full_output_path)
        if not os.path.exists(full_output_dirname):
            os.makedirs(full_output_dirname)

        sourcemap_path = full_output_path + ".map"
        sourcemap = ""

        try:
            if self.is_sourcemap_enabled:
                compiled, sourcemap = sass.compile(
                    filename=full_source_path,
                    source_map_filename=sourcemap_path,
                    output_filename_hint=full_output_path,
                    include_paths=self.load_paths,
                )
            else:
                compile_kwargs: Dict[str, Any] = {}
                if self.load_paths:
                    compile_kwargs["include_paths"] = self.load_paths
                if self.precision is not None:
                    compile_kwargs["precision"] = self.precision
                if self.output_style:
                    compile_kwargs["output_style"] = self.output_style
                compiled = sass.compile(filename=full_source_path, **compile_kwargs)
        except sass.CompileError as e:
            raise exceptions.StaticCompilationError(f"Could not compile {source_path}") from e

        compiled = encoding.force_str(compiled)
        sourcemap = encoding.force_str(sourcemap)

        utils.write_file(compiled, full_output_path)

        url_converter.convert_urls(full_output_path, source_path)

        if self.is_sourcemap_enabled:
            utils.write_file(sourcemap, sourcemap_path)
            utils.fix_sourcemap(sourcemap_path, source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source: str) -> str:
        try:
            compiled: str = sass.compile(string=source, indented=self.indented, include_paths=self.load_paths)
        except sass.CompileError as e:
            raise exceptions.StaticCompilationError("Could not compile source") from e

        return encoding.force_str(compiled)


# noinspection PyAbstractClass
class SASS(SCSS):

    name = "sass"
    input_extension = "sass"
    import_extensions = ("sass", "scss")

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*(?:\n|$)")

    indented = True
