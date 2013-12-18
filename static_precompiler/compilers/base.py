# coding: utf-8
from django.conf import settings
from django.contrib.staticfiles import finders
from static_precompiler.models import Dependency
from static_precompiler.settings import ROOT, ROOT, OUTPUT_DIR
from static_precompiler.utils import get_mtime
import logging
import os


logger = logging.getLogger("static_precompiler")


class BaseCompiler(object):

    supports_dependencies = False

    def is_supported(self, source_path):
        """ Return True iff provided source file type is supported by this precompiler.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: bool

        """
        raise NotImplementedError

    #noinspection PyMethodMayBeStatic
    def get_full_source_path(self, source_path):
        """ Return the full path to the given source file.
            Check if the source file exists.

        :param source_path: relative path to a source file
        :type source_path: basestring
        :returns: str
        :raises: ValueError

        """
        full_path = os.path.join(ROOT, source_path)

        if settings.DEBUG and not os.path.exists(full_path):
            # while developing it is more comfortable
            # searching for the source files rather then
            # doing collectstatics all the time
            full_path = finders.find(source_path)

            if full_path is None:
                raise ValueError("Can't find staticfile named: {0}".format(source_path))

        return full_path

    def get_output_filename(self, source_filename):
        """ Return the name of compiled file based on the name of source file.

        :param source_filename: name of a source file
        :type source_filename: str
        :returns: str

        """
        raise NotImplementedError

    def get_output_path(self, source_path):
        """ Get relative path to compiled file based for the given source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: str

        """
        source_dir = os.path.dirname(source_path)
        source_filename = os.path.basename(source_path)
        output_filename = self.get_output_filename(source_filename)
        return os.path.join(OUTPUT_DIR, source_dir, output_filename)

    def get_full_output_path(self, source_path):
        """ Get full path to compiled file based for the given source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: str

        """
        return os.path.join(ROOT, self.get_output_path(source_path))

    def get_source_mtime(self, source_path):
        """ Get the modification time of the source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: int

        """
        return get_mtime(self.get_full_source_path(source_path))

    def get_output_mtime(self, source_path):
        """ Get the modification time of the compiled file.
            Return None of compiled file does not exist.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: int, None

        """
        full_output_path = self.get_full_output_path(source_path)
        if not os.path.exists(full_output_path):
            return None
        return get_mtime(full_output_path)

    def should_compile(self, source_path, watch=False):
        """ Return True iff provided source file should be compiled.

        :param source_path: relative path to a source file
        :type source_path: str
        :param watch: whether the method was invoked from watch utility
        :type watch: bool
        :returns: bool

        """
        compiled_mtime = self.get_output_mtime(source_path)

        if compiled_mtime is None:
            return True

        source_mtime = self.get_source_mtime(source_path)

        if self.supports_dependencies:
            for dependency in self.get_dependencies(source_path):
                if compiled_mtime <= self.get_source_mtime(dependency):
                    return True

        return compiled_mtime <= source_mtime

    def get_source(self, source_path):
        """ Get the source code to be compiled.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: str

        """
        return open(self.get_full_source_path(source_path)).read()

    def write_output(self, output, source_path):
        """ Write the compiled output to a file.

        :param output: compiled code
        :type output: str
        :param source_path: relative path to a source file
        :type source_path: str

        """
        output_path = self.get_full_output_path(source_path)
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        compiled_file = open(output_path, "w+")
        compiled_file.write(output)
        compiled_file.close()

    def compile(self, source_path, watch=False):
        """ Compile the given source path and return relative path to the compiled file.
            Raise ValueError is the source file type is not supported.
            May raise a StaticCompilationError if something goes wrong with compilation.
        :param source_path: relative path to a source file
        :type source_path: str
        :param watch: whether the method was invoked from watch utility
        :type watch: bool

        :returns: str

        """
        if not self.is_supported(source_path):
            raise ValueError("'{0}' file type is not supported by '{1}'".format(
                source_path, self.__class__.__name__
            ))
        if self.should_compile(source_path, watch=watch):

            compiled = self.compile_file(source_path)
            compiled = self.postprocess(compiled, source_path)
            self.write_output(compiled, source_path)

            if self.supports_dependencies:
                self.update_dependencies(source_path, self.find_dependencies(source_path))

            logging.info("Compiled: '{0}'".format(source_path))

        return self.get_output_path(source_path)

    def compile_file(self, source_path):
        """ Compile the source file. Return the compiled code.
            May raise a StaticCompilationError if something goes wrong with compilation.

        :param source_path: path to the source file
        :type source_path: str
        :returns: str

        """
        raise NotImplementedError

    def compile_source(self, source):
        """ Compile the source code. May raise a StaticCompilationError
            if something goes wrong with compilation.

        :param source: source code
        :type source: str
        :returns: str

        """
        raise NotImplementedError

    #noinspection PyMethodMayBeStatic,PyUnusedLocal
    def postprocess(self, compiled, source_path):
        """ Post-process the compiled code.

        :param compiled: compiled code
        :type compiled: str
        :param source_path: relative path to a source file
        :type source_path: str
        :returns: str
        """
        return compiled

    def find_dependencies(self, source_path):
        """ Find the dependencies for the given source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: list
        """
        raise NotImplementedError

    #noinspection PyMethodMayBeStatic
    def get_dependencies(self, source_path):
        """ Get the saved dependencies for the given source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: list of str
        """
        return list(Dependency.objects.filter(
            source=source_path
        ).order_by("depends_on").values_list(
            "depends_on", flat=True
        ))

    #noinspection PyMethodMayBeStatic
    def get_dependents(self, source_path):
        """ Get a list of files that depends on the given source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :returns: list of str
        """
        return list(Dependency.objects.filter(
            depends_on=source_path
        ).order_by("source").values_list(
            "source", flat=True
        ))

    #noinspection PyMethodMayBeStatic
    def update_dependencies(self, source_path, dependencies):
        """ Updates the saved dependencies for the given source file.

        :param source_path: relative path to a source file
        :type source_path: str
        :param dependencies: list of files that source file depends on
        :type dependencies: list of str

        """
        if not dependencies:
            Dependency.objects.filter(source=source_path).delete()
        else:
            Dependency.objects.filter(
                source=source_path
            ).exclude(
                depends_on__in=dependencies,
            ).delete()
            for dependency in dependencies:
                Dependency.objects.get_or_create(
                    source=source_path,
                    depends_on=dependency,
                )

    def handle_changed_file(self, source_path):
        """ Handle the modification of the source file.

        :param source_path: relative path to a source file
        :type source_path: str

        """
        self.compile(source_path, watch=True)
        for dependent in self.get_dependents(source_path):
            self.compile(dependent, watch=True)
