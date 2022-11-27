import logging
import os
import posixpath
from typing import List, Optional

import django.core.exceptions
from django.contrib.staticfiles import finders
from django.utils import encoding, functional

from .. import models, mtime, settings, utils
from ..types import StrCollection

logger = logging.getLogger("static_precompiler")


__all__ = ("BaseCompiler",)


class BaseCompiler:

    name: str
    supports_dependencies: bool = False
    input_extension: str = ""
    output_extension: str = ""

    def is_supported(self, source_path: str) -> bool:
        """Return True iff provided source file type is supported by this precompiler.

        :param source_path: relative path to a source file
        """
        return os.path.splitext(source_path)[1].lstrip(".") == self.input_extension if self.input_extension else False

    # noinspection PyMethodMayBeStatic
    def get_full_source_path(self, source_path: str) -> str:
        """Return the full path to the given source file.
            Check if the source file exists.
            The returned path is OS-dependent.

        :param source_path: relative path to a source file
        :returns: full path to the source file (OS-dependent)
        :raises: ValueError
        """
        norm_source_path = utils.normalize_path(source_path.lstrip("/"))

        full_path: Optional[str] = None

        if settings.STATIC_ROOT:
            full_path = os.path.join(settings.STATIC_ROOT, norm_source_path)
            if os.path.exists(full_path):
                return full_path

        try:
            full_path = finders.find(norm_source_path)  # type: ignore
        except django.core.exceptions.SuspiciousOperation:
            pass

        if full_path is None:
            raise ValueError(f"Can't find staticfile named: {source_path}")

        return full_path

    def get_output_filename(self, source_filename: str) -> str:
        """Return the name of compiled file based on the name of source file.

        :param source_filename: name of a source file
        :returns: name of the compiled file
        """
        return f"{os.path.splitext(source_filename)[0]}.{self.output_extension}"

    def get_output_path(self, source_path: str) -> str:
        """Get relative path to compiled file based for the given source file.
            The returned path is in posix format.

        :param source_path: relative path to a source file
        :returns: relative path to the compiled file (in posix format)
        """
        source_dir = os.path.dirname(source_path.lstrip("/"))
        source_filename = os.path.basename(source_path)
        output_filename = self.get_output_filename(source_filename)
        return posixpath.join(settings.OUTPUT_DIR, source_dir, output_filename)

    def get_full_output_path(self, source_path: str) -> str:
        """Get full path to compiled file based for the given source file.
            The returned path is OS-dependent.

        :param source_path: relative path to a source file
        :returns: full path to the compiled file (OS-dependent)
        """
        return os.path.join(settings.ROOT, utils.normalize_path(self.get_output_path(source_path)))

    def get_source_mtime(self, source_path: str) -> float:
        """Get the modification time of the source file.

        :param source_path: relative path to a source file
        :returns: modification time of the source file
        """
        return mtime.get_mtime(self.get_full_source_path(source_path))

    def get_output_mtime(self, source_path: str) -> Optional[float]:
        """Get the modification time of the compiled file.
            Return None of compiled file does not exist.

        :param source_path: relative path to a source file
        :returns: modification time of the compiled file (if exists)
        """
        full_output_path = self.get_full_output_path(source_path)
        if not os.path.exists(full_output_path):
            return None
        return mtime.get_mtime(full_output_path)

    def should_compile(self, source_path: str, from_management: bool = False) -> bool:
        """Return True iff provided source file should be compiled.

        :param source_path: relative path to a source file
        :param from_management: whether the method was invoked from management command
        :returns: whether the source file should be compiled
        """
        if settings.DISABLE_AUTO_COMPILE and not from_management:
            return False

        compiled_mtime = self.get_output_mtime(source_path)

        if compiled_mtime is None:
            return True

        if compiled_mtime <= self.get_source_mtime(source_path):
            return True

        if self.supports_dependencies:
            for dependency in self.get_dependencies(source_path):
                dependency_mtime = self.get_source_mtime(dependency)
                if compiled_mtime <= dependency_mtime:
                    return True

        return False

    def get_source(self, source_path: str) -> str:
        """Get the source code to be compiled.

        :param source_path: relative path to a source file
        :returns: get the source code from the source file
        """
        return utils.read_file(self.get_full_source_path(source_path))

    def compile(self, source_path: str, from_management: bool = False, verbosity: int = 0) -> str:
        """Compile the given source path and return relative path to the compiled file.
            Raise ValueError is the source file type is not supported.
            May raise a StaticCompilationError if something goes wrong with compilation.
        :param source_path: relative path to a source file
        :param from_management: whether the method was invoked from management command
        :param verbosity: verbosity level
        :returns: path to the compiled file
        """
        if not self.is_supported(source_path):
            raise ValueError(f"'{source_path}' file type is not supported by '{self.__class__.__name__}'")

        compiled_path = self.get_output_path(source_path)

        if self.should_compile(source_path, from_management=from_management):

            compiled_path = self.compile_file(source_path)

            if self.supports_dependencies:
                self.update_dependencies(source_path, self.find_dependencies(source_path))

            message = f"Compiled '{source_path}' to '{compiled_path}'"

            if from_management and verbosity >= 1:
                print(message)
            else:
                logging.info(message)

        return compiled_path

    def compile_lazy(self, source_path: str) -> str:
        """Return a lazy object which, when translated to string, compiles the specified source path and returns
        the path to the compiled file.
        Raise ValueError is the source file type is not supported.
        May raise a StaticCompilationError if something goes wrong with compilation.
        :param source_path: relative path to a source file
        :returns: path to the compiled file
        """
        return encoding.force_str(self.compile(source_path))

    compile_lazy = functional.lazy(compile_lazy, str)

    def compile_file(self, source_path: str) -> str:
        """Compile the source file. Return the relative path to compiled file.
            May raise a StaticCompilationError if something goes wrong with compilation.

        :param source_path: path to the source file
        :returns: path to the compiled file
        """
        raise NotImplementedError

    def compile_source(self, source: str) -> str:
        """Compile the source code. May raise a StaticCompilationError
            if something goes wrong with compilation.

        :param source: source code
        :returns: compiled code
        """
        raise NotImplementedError

    def find_dependencies(self, source_path: str) -> List[str]:
        """Find the dependencies for the given source file.

        :param source_path: relative path to a source file
        :returns: list of paths to the dependencies
        """
        return []

    # noinspection PyMethodMayBeStatic
    def get_dependencies(self, source_path: str) -> List[str]:
        """Get the saved dependencies for the given source file.

        :param source_path: relative path to a source file
        :returns: list of paths to the dependencies
        """
        dependencies = []
        for dependency in models.Dependency.objects.filter(source=source_path).order_by("depends_on"):
            try:
                self.get_full_source_path(dependency.depends_on)
            except ValueError:
                # File referenced in Dependency can't be located. Remove the Dependency object.
                dependency.delete()
            else:
                dependencies.append(dependency.depends_on)
        return dependencies

    # noinspection PyMethodMayBeStatic
    def get_dependents(self, source_path: str) -> List[str]:
        """Get a list of files that depends on the given source file.

        :param source_path: relative path to a source file
        :returns: list of paths for the dependents
        """
        dependents = []
        for dependency in models.Dependency.objects.filter(depends_on=source_path).order_by("source"):
            try:
                self.get_full_source_path(dependency.source)
            except ValueError:
                # File referenced in Dependency can't be located. Remove the Dependency object.
                dependency.delete()
            else:
                dependents.append(dependency.source)
        return dependents

    # noinspection PyMethodMayBeStatic
    def update_dependencies(self, source_path: str, dependencies: StrCollection) -> None:
        """Updates the saved dependencies for the given source file.

        :param source_path: relative path to a source file
        :param dependencies: list of files that source file depends on
        """
        if not dependencies:
            models.Dependency.objects.filter(source=source_path).delete()
        else:
            models.Dependency.objects.filter(source=source_path).exclude(
                depends_on__in=dependencies,
            ).delete()
            for dependency in dependencies:
                models.Dependency.objects.get_or_create(
                    source=source_path,
                    depends_on=dependency,
                )
