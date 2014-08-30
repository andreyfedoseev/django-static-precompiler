from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.settings import COFFEESCRIPT_EXECUTABLE
from static_precompiler.utils import run_command


class CoffeeScript(BaseCompiler):

    name = "coffeescript"
    input_extension = "coffee"
    output_extension = "js"

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
