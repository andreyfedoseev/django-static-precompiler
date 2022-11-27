import os
import warnings
from typing import List, Optional

from .. import exceptions, utils
from . import base

__all__ = ("Babel",)


class Babel(base.BaseCompiler):

    name = "babel"
    input_extension = "es6"
    output_extension = "js"

    def __init__(
        self,
        executable: str = "babel",
        sourcemap_enabled: bool = False,
        modules: Optional[str] = None,
        plugins: Optional[str] = None,
        presets: Optional[str] = None,
    ):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        if modules:
            warnings.warn("'modules' option is removed in Babel 6.0. Use `plugins` instead.", DeprecationWarning)
        self.modules = modules
        self.plugins = plugins
        self.presets = presets
        super().__init__()

    def get_extra_args(self) -> List[str]:
        args = []

        if self.modules is not None:
            args += ["--modules", self.modules]

        if self.plugins is not None:
            args += ["--plugins", self.plugins]

        if self.presets is not None:
            args += ["--presets", self.presets]

        return args

    def compile_file(self, source_path: str) -> str:
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

        return_code, out, errors = utils.run_command(args)
        if return_code:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source: str) -> str:
        args = [
            self.executable,
        ] + self.get_extra_args()

        return_code, out, errors = utils.run_command(args, input=source)
        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out
