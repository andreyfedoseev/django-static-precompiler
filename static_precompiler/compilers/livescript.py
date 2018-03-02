import os

from . import base
from .. import exceptions, utils

__all__ = (
    "LiveScript",
)


class LiveScript(base.BaseCompiler):

    name = "livescript"
    input_extension = "ls"
    output_extension = "js"

    def __init__(self, executable='lsc', sourcemap_enabled=False):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        super(LiveScript, self).__init__()

    def compile_file(self, source_path):
        full_output_path = self.get_full_output_path(source_path)
        # LiveScript bug with source map if the folder isn't already present
        if not os.path.exists(os.path.dirname(full_output_path)):
            os.makedirs(os.path.dirname(full_output_path))
        args = [
            self.executable,
            "-c",
        ]
        if self.is_sourcemap_enabled:
            args.append("-m")
            args.append("linked")
        args.extend([
            "-o", os.path.dirname(full_output_path),
            self.get_full_source_path(source_path),
        ])
        return_code, out, errors = utils.run_command(args)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

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

    def find_dependencies(self, source_path):
        return []
