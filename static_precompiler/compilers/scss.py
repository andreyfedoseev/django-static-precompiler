from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.settings import SCSS_EXECUTABLE, SCSS_USE_COMPASS
from static_precompiler.utils import run_command, convert_urls
import os
import posixpath
import re


class SCSS(BaseCompiler):

    supports_dependencies = True

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*;")
    EXTENSION = ".scss"

    def is_supported(self, source_path):
        return source_path.endswith(self.EXTENSION)

    def get_output_filename(self, source_filename):
        return source_filename[:-len(self.EXTENSION)] + ".css"

    def should_compile(self, source_path, watch=False):
        # Do not auto-compile the files that start with "_"
        if watch and os.path.basename(source_path).startswith("_"):
            return False
        return super(SCSS, self).should_compile(source_path, watch)

    def compile_file(self, source_path):
        full_source_path = self.get_full_source_path(source_path)
        args = [
            SCSS_EXECUTABLE,
            "-C",
            full_source_path,
        ]

        if SCSS_USE_COMPASS:
            args.append("--compass")

        # `cwd` is a directory containing `source_path`. Ex: source_path = '1/2/3', full_source_path = '/abc/1/2/3' -> cwd = '/abc'
        cwd = os.path.normpath(os.path.join(full_source_path, *([".."] * len(source_path.split("/")))))
        out, errors = run_command(args, None, cwd=cwd)

        if errors:
            raise StaticCompilationError(errors)

        return out

    def compile_source(self, source):
        args = [
            SCSS_EXECUTABLE,
            "-s",
            "--scss",
            "-C",
        ]

        if SCSS_USE_COMPASS:
            args.append("--compass")

        out, errors = run_command(args, source)
        if errors:
            raise StaticCompilationError(errors)

        return out

    def postprocess(self, compiled, source_path):
        return convert_urls(compiled, source_path)

    def find_imports(self, source):
        """ Find the imported files in the source code.

        :param source: source code
        :type source: str
        :returns: list of str

        """
        imports = set()
        for import_string in self.IMPORT_RE.findall(source):
            for import_token in import_string.split(","):
                import_token = import_token.strip()
                if not import_token:
                    continue
                if import_token.startswith("url("):
                    continue
                if import_token[0] in ("'", '"'):
                    if import_token[-1] not in ("'", '"'):
                        continue
                    import_token = import_token.strip("'\"").strip()
                    if not import_token:
                        continue
                else:
                    parts = import_token.split(None, 1)
                    if len(parts) > 1:
                        continue
                    import_token = parts[0]
                if import_token.endswith(".css"):
                    continue
                if import_token.startswith("http://") or \
                   import_token.startswith("https://"):
                    continue
                imports.add(import_token)
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
    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*?\n")

    def compile_source(self, source):
        args = [
            SCSS_EXECUTABLE,
            "-s",
            "-C",
        ]

        if SCSS_USE_COMPASS:
            args.append("--compass")

        out, errors = run_command(args, source)
        if errors:
            raise StaticCompilationError(errors)

        return out
