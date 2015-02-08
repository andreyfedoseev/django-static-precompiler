from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.compilers.base import BaseCompiler
from static_precompiler.utils import run_command


class ES6To5(BaseCompiler):

    name = "es6"
    input_extension = "es6"
    output_extension = "js"

    def __init__(self, executable="6to5"):
        self.executable = executable
        super(ES6To5, self).__init__()

    def compile_file(self, source_path):
        return self.compile_source(self.get_source(source_path))

    def compile_source(self, source):
        args = [
            self.executable
        ]
        out, errors = run_command(args, source)
        if errors:
            raise StaticCompilationError(errors)

        return out
