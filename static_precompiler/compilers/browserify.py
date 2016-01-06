import os
import warnings

from static_precompiler import exceptions, utils

from . import base

__all__ = (
    "Browserify",
)


class Browserify(base.BaseCompiler):

    name = "browserify"
    input_extension = "jsx"
    output_extension = "js"

    def __init__(self, executable="browserify", transform=None):
        self.executable = executable
        self.transform = transform
        super(Browserify, self).__init__()

    def get_extra_args(self):
        args = []

        if self.transform:
            args += ["-t"] + self.transform.split(' ')

        return args

    def compile_file(self, source_path):
        args = [
            self.executable,
        ] + self.get_extra_args()

        full_output_path = self.get_full_output_path(source_path)

        full_output_dirname = os.path.dirname(full_output_path)
        if not os.path.exists(full_output_dirname):
            os.makedirs(full_output_dirname)

        args.append(self.get_full_source_path(source_path))
        args.extend(["-o", full_output_path])

        out, errors = utils.run_command(args)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source):
        args = [
            self.executable,
            "-",
        ] + self.get_extra_args()

        out, errors = utils.run_command(args, source)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return out
