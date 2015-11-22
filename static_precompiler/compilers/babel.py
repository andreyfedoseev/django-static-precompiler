import json
import os
import posixpath
import warnings

from static_precompiler import exceptions, utils

from . import base

__all__ = (
    "Babel",
)


class Babel(base.BaseCompiler):

    name = "babel"
    input_extension = "es6"
    output_extension = "js"

    def __init__(self, executable="babel", sourcemap_enabled=False, modules=None, plugins=None):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        if modules:
            warnings.warn("'modules' option is removed in Babel 6.0. Use `plugins` instead.", DeprecationWarning)
        self.modules = modules
        self.plugins = plugins
        super(Babel, self).__init__()

    def get_extra_args(self):
        args = []

        if self.modules is not None:
            args += ["--modules", self.modules]

        if self.plugins is not None:
            args += ["--plugins", self.plugins]

        return args

    def compile_file(self, source_path):
        args = [
            self.executable,
        ] + self.get_extra_args()

        if self.is_sourcemap_enabled:
            args.append("-s")

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
            self.executable,
        ] + self.get_extra_args()

        out, errors = utils.run_command(args, source)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return out
