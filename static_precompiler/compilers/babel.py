import json
import os
import posixpath

from static_precompiler import exceptions, utils

from . import base

__all__ = (
    "Babel",
)


class Babel(base.BaseCompiler):

    name = "babel"
    input_extension = "es6"
    output_extension = "js"

    def __init__(self, executable="babel", sourcemap_enabled=False, modules=None):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        self.modules = modules
        super(Babel, self).__init__()

    def compile_file(self, source_path):
        args = [
            self.executable,
        ]

        if self.is_sourcemap_enabled:
            args.append("-s")

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

        if self.is_sourcemap_enabled:
            sourcemap_full_path = full_output_path + ".map"

            with open(sourcemap_full_path) as sourcemap_file:
                sourcemap = json.loads(sourcemap_file.read())

            # Babel can't add correct relative paths in source map when the compiled file
            # is not in the same dir as the source file. We fix it here.
            sourcemap["sourceRoot"] = "../" * len(source_path.split("/")) + posixpath.dirname(source_path)
            sourcemap["sources"] = [os.path.basename(source) for source in sourcemap["sources"]]
            sourcemap["file"] = posixpath.basename(os.path.basename(full_output_path))

            with open(sourcemap_full_path, "w") as sourcemap_file:
                sourcemap_file.write(json.dumps(sourcemap))

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
