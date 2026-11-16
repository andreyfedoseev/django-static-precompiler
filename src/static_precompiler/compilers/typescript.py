import os
import tempfile
from pathlib import Path
from typing import List, Optional

from .. import exceptions, utils
from . import base

__all__ = ("TypeScript",)


class TypeScript(base.BaseCompiler):
    name = "typescript"
    input_extension = "ts"
    output_extension = "js"

    def __init__(
        self,
        executable: str = "tsc",
        sourcemap_enabled: bool = False,
        target: Optional[str] = None,
        module: Optional[str] = None,
    ):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        self.target = target
        self.module = module
        super().__init__()

    def get_extra_args(self) -> List[str]:
        args = []
        if self.target is not None:
            args.extend(["--target", self.target])
        if self.module is not None:
            args.extend(["--module", self.module])
        return args

    def compile_file(self, source_path: str) -> str:
        full_source_path = self.get_full_source_path(source_path)
        full_output_path = self.get_full_output_path(source_path)
        output_dir = os.path.dirname(full_output_path)
        os.makedirs(output_dir, exist_ok=True)

        args = [self.executable, *self.get_extra_args()]
        if self.is_sourcemap_enabled:
            args.append("--sourceMap")
        args.extend(["--outDir", output_dir, full_source_path])

        return_code, out, errors = utils.run_command(args)
        if return_code:
            raise exceptions.StaticCompilationError(errors or out)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source: str) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "source.ts"
            output_path = Path(temp_dir) / "source.js"
            source_path.write_text(source, encoding="utf-8")

            args = [
                self.executable,
                *self.get_extra_args(),
                "--outDir",
                temp_dir,
                str(source_path),
            ]
            return_code, out, errors = utils.run_command(args)
            if return_code:
                raise exceptions.StaticCompilationError(errors or out)

            if not output_path.exists():
                raise exceptions.StaticCompilationError("TypeScript compilation produced no output file.")

            return output_path.read_text(encoding="utf-8")
