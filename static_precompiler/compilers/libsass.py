import os
import re

import sass
from django.utils import encoding

from . import scss
from .. import exceptions, url_converter, utils

__all__ = (
    "SCSS",
    "SASS",
)


class SCSS(scss.SCSS):

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*;", re.DOTALL)
    indented = False
    is_compass_enabled = False

    def __init__(self, sourcemap_enabled=False, load_paths=None, precision=None, output_style=None):
        self.is_sourcemap_enabled = sourcemap_enabled
        self.precision = precision
        self.output_style = output_style
        if load_paths is None:
            self.load_paths = []
        elif not isinstance(load_paths, (list, tuple)):
            raise ValueError("load_paths option must be an iterable object (list, tuple)")
        else:
            self.load_paths = load_paths
        super(scss.SCSS, self).__init__()

    def compile_file(self, source_path):
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
                    include_paths=self.load_paths
                )
            else:
                compile_kwargs = {}
                if self.load_paths:
                    compile_kwargs["include_paths"] = self.load_paths
                if self.precision:
                    compile_kwargs["precision"] = self.precision
                if self.output_style:
                    compile_kwargs["output_style"] = self.output_style
                compiled = sass.compile(filename=full_source_path, **compile_kwargs)
        except sass.CompileError as e:
            raise exceptions.StaticCompilationError(encoding.force_str(e))

        compiled = encoding.force_str(compiled)
        sourcemap = encoding.force_str(sourcemap)

        utils.write_file(compiled, full_output_path)

        url_converter.convert_urls(full_output_path, source_path)

        if self.is_sourcemap_enabled:
            utils.write_file(sourcemap, sourcemap_path)
            utils.fix_sourcemap(sourcemap_path, source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source):
        try:
            compiled = sass.compile(string=source, indented=self.indented, include_paths=self.load_paths)
        except sass.CompileError as e:
            raise exceptions.StaticCompilationError(encoding.force_str(e))

        compiled = encoding.force_str(compiled)

        return compiled


# noinspection PyAbstractClass
class SASS(SCSS):

    name = "sass"
    input_extension = "sass"
    import_extensions = ("sass", "scss")

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*(?:\n|$)")

    indented = True
