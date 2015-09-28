import os

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
        args = [
            self.executable,
            "-c",
            "-o", os.path.dirname(self.get_full_output_path(source_path)),
            self.get_full_source_path(source_path),
        ]
        out, errors = utils.run_command(args)
        if errors:
            raise exceptions.StaticCompilationError(errors)
        return self.get_output_path(source_path)

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
