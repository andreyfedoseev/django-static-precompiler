from static_precompiler import exceptions, utils

from . import base

__all__ = (
    "Babel",
)


class Babel(base.BaseCompiler):

    name = "babel"
    input_extension = "es6"
    output_extension = "js"

    def __init__(self, executable="babel"):
        self.executable = executable
        super(Babel, self).__init__()

    def compile_file(self, source_path):
        return self.compile_source(self.get_source(source_path))

    def compile_source(self, source):
        args = [
            self.executable
        ]
        out, errors = utils.run_command(args, source)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return out
