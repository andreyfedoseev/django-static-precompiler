import json
import os
import posixpath

from static_precompiler import exceptions, utils

from . import base

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
        out, errors = utils.run_command(args)

        if errors:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            # Livescript writes source maps to compiled.js.map
            sourcemap_full_path = full_output_path + ".map"

            with open(sourcemap_full_path) as sourcemap_file:
                sourcemap = json.loads(sourcemap_file.read())

            # LiveScript, unlike SASS, can't add correct relative paths in source map when the compiled file
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
