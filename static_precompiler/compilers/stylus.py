import os
import posixpath
import re

from . import base
from .. import exceptions, url_converter, utils

__all__ = (
    "Stylus",
)


class Stylus(base.BaseCompiler):

    name = "stylus"
    input_extension = "styl"
    output_extension = "css"
    supports_dependencies = True

    IMPORT_RE = re.compile(r"@(?:import|require)\s+(.+?)\s*$", re.MULTILINE)

    def __init__(self, executable="stylus", sourcemap_enabled=False):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        super(Stylus, self).__init__()

    def compile_source(self, source):
        args = [
            self.executable,
            "-p",
        ]
        return_code, out, errors = utils.run_command(args, input=source)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out

    def compile_file(self, source_path):
        full_source_path = self.get_full_source_path(source_path)
        full_output_path = self.get_full_output_path(source_path)
        args = [
            self.executable,
        ]
        if self.is_sourcemap_enabled:
            args.append("-m")
        args.extend([
            full_source_path,
            "-o", os.path.dirname(full_output_path),
        ])

        full_output_dirname = os.path.dirname(full_output_path)
        if not os.path.exists(full_output_dirname):
            os.makedirs(full_output_dirname)

        # `cwd` is a directory containing `source_path`.
        # Ex: source_path = '1/2/3', full_source_path = '/abc/1/2/3' -> cwd = '/abc'
        cwd = os.path.normpath(os.path.join(full_source_path, *([".."] * len(source_path.split("/")))))
        return_code, out, errors = utils.run_command(args, cwd=cwd)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        url_converter.convert_urls(full_output_path, source_path)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def find_imports(self, source):
        """ Find the imported files in the source code.

        :param source: source code
        :type source: str
        :returns: list of str

        """
        imports = set()
        for import_string in self.IMPORT_RE.findall(source):
            import_string = import_string.strip("'").strip('"').strip()
            if not import_string:
                continue
            if import_string.startswith("url("):
                continue
            if import_string.endswith(".css"):
                continue
            if import_string.startswith("http://") or import_string.startswith("https://"):
                continue
            imports.add(import_string)
        return sorted(imports)

    def locate_imported_file(self, source_dir, import_path):
        """ Locate the imported file in the source directory.
            Return the path to the imported file relative to STATIC_ROOT

        :param source_dir: source directory
        :type source_dir: str
        :param import_path: path to the imported file
        :type import_path: str
        :returns: str

        """
        path = posixpath.normpath(posixpath.join(source_dir, import_path))

        try:
            self.get_full_source_path(path)
        except ValueError:
            raise exceptions.StaticCompilationError(
                "Can't locate the imported file: {0}".format(import_path)
            )
        return path

    def find_dependencies(self, source_path):
        source = self.get_source(source_path)
        source_dir = posixpath.dirname(source_path)
        dependencies = set()
        imported_files = set()
        for import_path in self.find_imports(source):
            if import_path.endswith(".styl"):
                # @import "foo.styl"
                imported_files.add(self.locate_imported_file(source_dir, import_path))
            elif import_path.endswith("/*"):
                # @import "foo/*"
                imported_dir = posixpath.join(source_dir, import_path[:-2])
                try:
                    imported_dir_full_path = self.get_full_source_path(imported_dir)
                except ValueError:
                    raise exceptions.StaticCompilationError(
                        "Can't locate the imported directory: {0}".format(import_path)
                    )
                if not os.path.isdir(imported_dir_full_path):
                    raise exceptions.StaticCompilationError(
                        "Imported path is not a directory: {0}".format(import_path)
                    )
                for filename in os.listdir(imported_dir_full_path):
                    if filename.endswith(".styl"):
                        imported_files.add(self.locate_imported_file(imported_dir, filename))
            else:
                try:
                    # @import "foo" -> @import "foo/index.styl"
                    imported_dir = posixpath.join(source_dir, import_path)
                    imported_dir_full_path = self.get_full_source_path(imported_dir)
                    if os.path.isdir(imported_dir_full_path):
                        imported_files.add(self.locate_imported_file(imported_dir, "index.styl"))
                except ValueError:
                    # @import "foo" -> @import "foo.styl"
                    imported_files.add(self.locate_imported_file(source_dir, import_path + ".styl"))

        dependencies.update(imported_files)
        for imported_file in imported_files:
            dependencies.update(self.find_dependencies(imported_file))

        return sorted(dependencies)
