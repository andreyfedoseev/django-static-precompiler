import os

from static_precompiler import exceptions, utils

from . import base

__all__ = (
    "Babel",
)


class Babel(base.BaseCompiler):

    name = "babel"
    input_extension = "es6"
    output_extension = "js"

    def __init__(self, executable="babel", modules=None):
        self.executable = executable
        self.modules = modules
        super(Babel, self).__init__()

    def compile_file(self, source_path):
        args = [
            self.executable
        ]

        if self.modules is not None:
            args.extend(["--modules", self.modules])

        full_output_path = self.get_full_output_path(source_path)

        full_output_dirname = os.path.dirname(full_output_path)
        if not os.path.exists(full_output_dirname):
            os.makedirs(full_output_dirname)

        args.extend(["-o", full_output_path])
        args.append(self.get_full_source_path(source_path))

        out, errors = utils.run_command(args)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return self.get_output_path(source_path)

    def compile_source(self, source):
        args = [
            self.executable
        ]

        if self.modules is not None:
            args.extend(["--modules", self.modules])

        out, errors = utils.run_command(args, source)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return out
