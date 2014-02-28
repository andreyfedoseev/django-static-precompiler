from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.settings import COFFEESCRIPT_EXECUTABLE
from static_precompiler.utils import run_command


class CoffeeScript(BaseCompiler):

    def is_supported(self, source_path):
        return source_path.endswith(".coffee")

    def get_output_filename(self, source_filename):
        return source_filename[:-7] + ".js"

    def compile_file(self, source_path):
        return self.compile_source(self.get_source(source_path))

    def compile_source(self, source):
        args = [
            COFFEESCRIPT_EXECUTABLE,
            "-c",
            "-s",
            "-p",
        ]
        out, errors = run_command(args, source)
        if errors:
            raise StaticCompilationError(errors)

        return out
