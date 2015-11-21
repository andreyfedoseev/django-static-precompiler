import json
import os
import posixpath

from static_precompiler import exceptions, utils

from . import base

__all__ = (
    "Handlebars",
)


class Handlebars(base.BaseCompiler):

    name = "handlebars"
    input_extensions = ("hbs", "handlebars", )
    output_extension = "js"

    def is_supported(self, source_path):
        return os.path.splitext(source_path)[1].lstrip(".") in self.input_extensions

    def __init__(self, executable="handlebars", sourcemap_enabled=False, known_helpers=None,
                 namespace=None, simple=False):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        if known_helpers is None:
            self.known_helpers = []
        elif not hasattr(known_helpers, "__iter__"):
            raise ValueError("known_helpers option must be an iterable object (list, tuple)")
        else:
            self.known_helpers = known_helpers
        self.namespace = namespace
        self.simple = simple
        super(Handlebars, self).__init__()

    def get_extra_args(self):
        args = []

        for helper in self.known_helpers:
            args += ["-k", helper]

        if self.namespace:
            args += ["-n", self.namespace]

        if self.simple:
            args.append("-s")

        return args

    def compile_file(self, source_path):
        full_output_path = self.get_full_output_path(source_path)
        output_dir = os.path.dirname(full_output_path)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        template_extension = os.path.splitext(source_path)[1].lstrip(".")

        args = [
            self.executable,
            self.get_full_source_path(source_path),
            "-e", template_extension,
            "-f", full_output_path,
        ] + self.get_extra_args()

        if self.is_sourcemap_enabled:
            args += ["--map", full_output_path + ".map"]

        out, errors = utils.run_command(args)

        if errors:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            sourcemap_full_path = full_output_path + ".map"

            with open(sourcemap_full_path) as sourcemap_file:
                sourcemap = json.loads(sourcemap_file.read())

            # Handlebars, unlike SASS, can't add correct relative paths in source map when the compiled file
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
            "-i", "-",
        ] + self.get_extra_args()

        out, errors = utils.run_command(args, source)
        if errors:
            raise exceptions.StaticCompilationError(errors)

        return out
