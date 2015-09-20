from static_precompiler import exceptions, settings, utils

from . import base

__all__ = (
    "CoffeeScript",
)


class CoffeeScript(base.BaseCompiler):

    name = "coffeescript"
    input_extension = "coffee"
    output_extension = "js"

    def __init__(self, executable=settings.COFFEESCRIPT_EXECUTABLE):
        self.executable = executable
        super(CoffeeScript, self).__init__()

    def compile_file(self, source_path):
        return self.compile_source(self.get_source(source_path))

    def compile_source(self, source):
        args = [
            self.executable,
            "-c",
            "-s",
            "-p",
        ]
        out, errors = utils.run_command(args, source)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return out

    def find_dependencies(self, source_path):
        return []
