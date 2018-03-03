import os

from . import base
from .. import exceptions, utils

__all__ = (
    "CoffeeScript",
)


class CoffeeScript(base.BaseCompiler):

    name = "coffeescript"
    input_extension = "coffee"
    output_extension = "js"

    def __init__(self, executable="coffee", sourcemap_enabled=False):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        super(CoffeeScript, self).__init__()

    def compile_file(self, source_path):
        full_output_path = self.get_full_output_path(source_path)
        args = [
            self.executable,
            "-c",
        ]
        if self.is_sourcemap_enabled:
            args.append("-m")
        args.extend([
            "-o", os.path.dirname(full_output_path),
            self.get_full_source_path(source_path),
        ])
        return_code, out, errors = utils.run_command(args)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(os.path.splitext(full_output_path)[0] + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source):
        args = [
            self.executable,
            "-c",
            "-s",
            "-p",
        ]
        return_code, out, errors = utils.run_command(args, source)
        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out
