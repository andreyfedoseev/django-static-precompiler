import os
import posixpath
import re
from typing import Dict, List, Optional

from .. import exceptions, url_converter, utils
from ..types import StrCollection
from . import base

__all__ = ("LESS",)


class LESS(base.BaseCompiler):

    name = "less"
    supports_dependencies = True
    input_extension = "less"
    output_extension = "css"

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*;", re.DOTALL)
    IMPORT_ITEM_RE = re.compile(r"([\"'])(.+?)\1")

    def __init__(
        self,
        executable: str = "lessc",
        sourcemap_enabled: bool = False,
        include_path: Optional[StrCollection] = None,
        clean_css: bool = False,
        global_vars: Optional[Dict[str, str]] = None,
    ):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        self.include_path: Optional[str] = None
        if include_path is not None:
            self.include_path = ";".join(include_path)
        self.clean_css = clean_css
        self.global_vars = global_vars
        super().__init__()

    def should_compile(self, source_path: str, from_management: bool = False) -> bool:
        # Do not compile the files that start with "_" if run from management
        if from_management and os.path.basename(source_path).startswith("_"):
            return False
        return super().should_compile(source_path, from_management)

    def compile_file(self, source_path: str) -> str:
        full_source_path = self.get_full_source_path(source_path)
        full_output_path = self.get_full_output_path(source_path)

        # `cwd` is a directory containing `source_path`.
        # Ex: source_path = '1/2/3', full_source_path = '/abc/1/2/3' -> cwd = '/abc'
        cwd = os.path.normpath(os.path.join(full_source_path, *([".."] * len(source_path.split("/")))))

        args = [self.executable]
        if self.is_sourcemap_enabled:
            args.append("--source-map")
        if self.include_path:
            args.append(f"--include-path={self.include_path}")
        if self.clean_css:
            args.append("--clean-css")
        if self.global_vars:
            for variable_name, variable_value in self.global_vars.items():
                args.append(f"--global-var={variable_name}={variable_value}")

        args.extend([self.get_full_source_path(source_path), full_output_path])
        return_code, out, errors = utils.run_command(args, cwd=cwd)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        url_converter.convert_urls(full_output_path, source_path)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source: str) -> str:
        args = [self.executable, "-"]
        if self.include_path:
            args.append(f"--include-path={self.include_path}")

        return_code, out, errors = utils.run_command(args, input=source)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out

    def find_imports(self, source: str) -> List[str]:
        """Find the imported files in the source code.

        :param source: source code
        """
        imports = set()
        for import_string in self.IMPORT_RE.findall(source):
            import_string = import_string.strip()
            if import_string.startswith("(css)"):
                continue
            if "url(" in import_string:
                continue
            match = self.IMPORT_ITEM_RE.search(import_string)
            if not match:
                continue
            import_item = match.groups()[1].strip()
            if not import_item:
                continue
            if import_item.endswith(".css") and not import_string.startswith("(inline)"):
                continue
            imports.add(import_item)

        return sorted(imports)

    def locate_imported_file(self, source_dir: str, import_path: str) -> str:
        """Locate the imported file in the source directory.
            Return the relative path to the imported file in posix format.

        :param source_dir: source directory
        :param import_path: path to the imported file
        """
        if not import_path.endswith("." + self.input_extension):
            import_path += "." + self.input_extension
        path = posixpath.normpath(posixpath.join(source_dir, import_path))

        try:
            self.get_full_source_path(path)
            return path
        except ValueError:
            pass

        filename = posixpath.basename(import_path)
        if filename[0] != "_":
            path = posixpath.normpath(
                posixpath.join(
                    source_dir,
                    posixpath.dirname(import_path),
                    "_" + filename,
                )
            )

        try:
            self.get_full_source_path(path)
            return path
        except ValueError:
            pass

        raise exceptions.StaticCompilationError(f"Can't locate the imported file: {import_path}")

    def find_dependencies(self, source_path: str) -> List[str]:
        source = self.get_source(source_path)
        source_dir = posixpath.dirname(source_path)
        dependencies = set()
        for import_path in self.find_imports(source):
            import_path = self.locate_imported_file(source_dir, import_path)
            dependencies.add(import_path)
            dependencies.update(self.find_dependencies(import_path))
        return sorted(dependencies)
