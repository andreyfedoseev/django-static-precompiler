from static_precompiler import settings
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.utils import run_command, convert_urls
import os
import posixpath
import re


class SCSS(BaseCompiler):

    supports_dependencies = True

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*;", re.DOTALL)
    EXTENSION = ".scss"

    # noinspection PyMethodMayBeStatic
    def compass_enabled(self):
        return settings.SCSS_USE_COMPASS

    def is_supported(self, source_path):
        return source_path.endswith(self.EXTENSION)

    def get_output_filename(self, source_filename):
        return source_filename[:-len(self.EXTENSION)] + ".css"

    def should_compile(self, source_path, from_management=False):
        # Do not compile the files that start with "_" if run from management
        if from_management and os.path.basename(source_path).startswith("_"):
            return False
        return super(SCSS, self).should_compile(source_path, from_management)

    def compile_file(self, source_path):
        full_source_path = self.get_full_source_path(source_path)
        args = [
            settings.SCSS_EXECUTABLE,
            "-C",
            full_source_path,
        ]

        if self.compass_enabled():
            args.append("--compass")

        # `cwd` is a directory containing `source_path`. Ex: source_path = '1/2/3', full_source_path = '/abc/1/2/3' -> cwd = '/abc'
        cwd = os.path.normpath(os.path.join(full_source_path, *([".."] * len(source_path.split("/")))))
        out, errors = run_command(args, None, cwd=cwd)

        if errors:
            raise StaticCompilationError(errors)

        return out

    def compile_source(self, source):
        args = [
            settings.SCSS_EXECUTABLE,
            "-s",
            "--scss",
            "-C",
        ]

        if self.compass_enabled():
            args.append("--compass")

        out, errors = run_command(args, source)
        if errors:
            raise StaticCompilationError(errors)

        return out

    def postprocess(self, compiled, source_path):
        return convert_urls(compiled, source_path)

    def parse_import_string(self, import_string):
        """ Extract import items from import string.
        :param import_string: import string
        :type import_string: str
        :returns: list of str
        """
        items = []
        item = ""
        in_quotes = False
        quote = ""
        in_parentheses = False
        item_allowed = True

        for char in import_string:

            if char == ")":
                in_parentheses = False
                continue

            if in_parentheses:
                continue

            if char == "(":
                item = ""
                in_parentheses = True
                continue

            if char == ",":
                if in_quotes:
                    item += char
                else:
                    if item:
                        items.append(item)
                        item = ""
                    item_allowed = True
                continue

            if char in " \t\n\r\f\v":
                if in_quotes:
                    item += char
                elif item:
                    items.append(item)
                    item_allowed = False
                    item = ""
                continue

            if char in "\"'":
                if in_quotes:
                    if char == quote:
                        # Close quote
                        in_quotes = False
                    else:
                        item += char
                else:
                    in_quotes = True
                    quote = char
                continue

            if not item_allowed:
                break

            item += char

        if item:
            items.append(item)

        return sorted(items)

    def find_imports(self, source):
        """ Find the imported files in the source code.

        :param source: source code
        :type source: str
        :returns: list of str

        """
        imports = set()
        for import_string in self.IMPORT_RE.findall(source):
            for import_item in self.parse_import_string(import_string):
                import_item = import_item.strip()
                if not import_item:
                    continue
                if import_item.endswith(".css"):
                    continue
                if import_item.startswith("http://") or \
                   import_item.startswith("https://"):
                    continue
                if self.compass_enabled() and (import_item in ("compass", "compass.scss") or import_item.startswith("compass/")):
                    # Ignore compass imports if Compass is enabled.
                    continue
                imports.add(import_item)
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
        if not import_path.endswith(self.EXTENSION):
            import_path += self.EXTENSION
        path = posixpath.normpath(posixpath.join(source_dir, import_path))

        try:
            self.get_full_source_path(path)
            return path
        except ValueError:
            pass

        filename = posixpath.basename(import_path)
        if filename[0] != "_":
            path = posixpath.normpath(posixpath.join(
                source_dir,
                posixpath.dirname(import_path),
                "_" + filename,
            ))

        try:
            self.get_full_source_path(path)
            return path
        except ValueError:
            pass

        raise StaticCompilationError(
            "Can't locate the imported file: {0}".format(import_path)
        )

    def find_dependencies(self, source_path):
        source = self.get_source(source_path)
        source_dir = posixpath.dirname(source_path)
        dependencies = set()
        for import_path in self.find_imports(source):
            import_path = self.locate_imported_file(source_dir, import_path)
            dependencies.add(import_path)
            dependencies.update(self.find_dependencies(import_path))
        return sorted(dependencies)


class SASS(SCSS):

    EXTENSION = ".sass"
    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*(?:\n|$)")

    def compile_source(self, source):
        args = [
            settings.SCSS_EXECUTABLE,
            "-s",
            "-C",
        ]

        if self.compass_enabled():
            args.append("--compass")

        out, errors = run_command(args, source)
        if errors:
            raise StaticCompilationError(errors)

        return out
