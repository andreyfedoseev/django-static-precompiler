from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.settings import LESS_EXECUTABLE, ROOT
from static_precompiler.utils import run_command, convert_urls
import os
import re


class LESS(BaseCompiler):

    supports_dependencies = True

    IMPORT_RE = re.compile(r"@import\s+(?:\(less\)\s+)?(.+?)\s*;")
    EXTENSION = ".less"

    def is_supported(self, source_path):
        return source_path.endswith(self.EXTENSION)

    def get_output_filename(self, source_filename):
        return source_filename[:-len(self.EXTENSION)] + ".css"

    def should_compile(self, source_path, watch=False):
        # Do not auto-compile the files that start with "_"
        if watch and os.path.basename(source_path).startswith("_"):
            return False
        return super(LESS, self).should_compile(source_path, watch)

    def compile_file(self, source_path):
        command = "{0} {1}".format(
            LESS_EXECUTABLE,
            self.get_full_source_path(source_path)
        )

        out, errors = run_command(command, None)
        if errors:
            raise StaticCompilationError(errors)

        return out

    def compile_source(self, source):
        command = "{0} -".format(LESS_EXECUTABLE)

        out, errors = run_command(command, source)

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
            Return the path to the imported file relative to ROOT

        :param source_dir: source directory
        :type source_dir: str
        :param import_path: path to the imported file
        :type import_path: str
        :returns: str

        """
        if not import_path.endswith(self.EXTENSION):
            import_path += self.EXTENSION
        path = os.path.normpath(os.path.join(source_dir, import_path))

        if os.path.exists(os.path.join(ROOT, path)):
            return path

        filename = os.path.basename(import_path)
        if filename[0] != "_":
            path = os.path.normpath(os.path.join(
                source_dir,
                os.path.dirname(import_path),
                "_" + filename,
            ))
            if os.path.exists(os.path.join(ROOT, path)):
                return path

        raise StaticCompilationError(
            "Can't locate the imported file: {0}".format(import_path)
        )

    def find_dependencies(self, source_path):
        source = self.get_source(source_path)
        source_dir = os.path.dirname(source_path)
        dependencies = set()
        for import_path in self.find_imports(source):
            import_path = self.locate_imported_file(source_dir, import_path)
            dependencies.add(import_path)
            dependencies.update(self.find_dependencies(import_path))
        return sorted(dependencies)
