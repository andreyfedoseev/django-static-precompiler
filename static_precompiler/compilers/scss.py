import os
import posixpath
import re

from . import base
from .. import exceptions, url_converter, utils

__all__ = (
    "SCSS",
    "SASS",
)


class SCSS(base.BaseCompiler):

    name = "scss"
    supports_dependencies = True
    input_extension = "scss"
    output_extension = "css"
    import_extensions = ("scss", "sass")

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*;", re.DOTALL)

    def __init__(self, executable="sass", sourcemap_enabled=False, compass_enabled=False, load_paths=None,
                 precision=None, output_style=None):
        self.executable = executable
        self.is_sourcemap_enabled = sourcemap_enabled
        self.is_compass_enabled = compass_enabled
        self.precision = precision
        self.output_style = output_style
        if load_paths is None:
            self.load_paths = []
        elif not isinstance(load_paths, (list, tuple)):
            raise ValueError("load_paths option must be an iterable object (list, tuple)")
        else:
            self.load_paths = load_paths
        super(SCSS, self).__init__()

    def get_extra_args(self):
        args = []

        for path in self.load_paths:
            args += ["-I", path]

        if self.is_compass_enabled:
            args.append("--compass")

        if self.precision:
            args += ["--precision", str(self.precision)]

        if self.output_style:
            args += ["-t", self.output_style]

        return args

    def should_compile(self, source_path, from_management=False):
        # Do not compile the files that start with "_" if run from management
        if from_management and os.path.basename(source_path).startswith("_"):
            return False
        return super(SCSS, self).should_compile(source_path, from_management)

    def compile_file(self, source_path):
        full_source_path = self.get_full_source_path(source_path)
        full_output_path = self.get_full_output_path(source_path)
        args = [
            self.executable,
            "--sourcemap={0}".format("auto" if self.is_sourcemap_enabled else "none"),
        ] + self.get_extra_args()

        args.extend([
            self.get_full_source_path(source_path),
            full_output_path,
        ])

        full_output_dirname = os.path.dirname(full_output_path)
        if not os.path.exists(full_output_dirname):
            os.makedirs(full_output_dirname)

        # `cwd` is a directory containing `source_path`.
        # Ex: source_path = '1/2/3', full_source_path = '/abc/1/2/3' -> cwd = '/abc'
        cwd = os.path.normpath(os.path.join(full_source_path, *([".."] * len(source_path.split("/")))))
        return_code, out, errors = utils.run_command(args, None, cwd=cwd)

        if return_code:
            if os.path.exists(full_output_path):
                os.remove(full_output_path)
            raise exceptions.StaticCompilationError(errors)

        url_converter.convert_urls(full_output_path, source_path)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(full_output_path + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source):
        args = [
            self.executable,
            "-s",
        ] + self.get_extra_args()

        if self.executable.endswith("sass"):
            args.append("--scss")

        return_code, out, errors = utils.run_command(args, source)
        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out

    # noinspection PyMethodMayBeStatic
    def parse_import_string(self, import_string):
        """ Extract import items from import string.
        :param import_string: import string
        :type import_string: str
        :returns: list of str
        """
        items = []
        item = ""
        in_quotes = False
        quote = ""
        in_parentheses = False
        item_allowed = True

        for char in import_string:

            if char == ")":
                in_parentheses = False
                continue

            if in_parentheses:
                continue

            if char == "(":
                item = ""
                in_parentheses = True
                continue

            if char == ",":
                if in_quotes:
                    item += char
                else:
                    if item:
                        items.append(item)
                        item = ""
                    item_allowed = True
                continue

            if char in " \t\n\r\f\v":
                if in_quotes:
                    item += char
                elif item:
                    items.append(item)
                    item_allowed = False
                    item = ""
                continue

            if char in "\"'":
                if in_quotes:
                    if char == quote:
                        # Close quote
                        in_quotes = False
                    else:
                        item += char
                else:
                    in_quotes = True
                    quote = char
                continue

            if not item_allowed:
                break

            item += char

        if item:
            items.append(item)

        return sorted(items)

    def strip_comments(self, source):
        """ Strip comments from source, it does not remove comments inside
        strings or comments inside functions calls.

        Contribution taken from and added function call pattern
        https://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files

        :param source: source code
        :type source: str
        :returns: str

        """
        pattern = r"(\".*?\"|\'.*?\'|\(.*?\))|(\s*/\*.*?\*/|\s*//[^\r\n]*$)"
        # first group captures quoted sources (double or single)
        # second group captures comments (//single-line or /* multi-line */)
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

        def _replacer(match):
            # if the 2nd group (capturing comments) is not None,
            # it means we have captured a non-quoted (real) comment source.
            if match.group(2) is not None:
                return ""  # so we will return empty to remove the comment
            else:  # otherwise, we will return the 1st group
                return match.group(1)  # captured quoted-source or function call
        return regex.sub(_replacer, source)

    def find_imports(self, source):
        """ Find the imported files in the source code.

        :param source: source code
        :type source: str
        :returns: list of str

        """
        source = self.strip_comments(source)
        imports = set()
        for import_string in self.IMPORT_RE.findall(source):
            for import_item in self.parse_import_string(import_string):
                import_item = import_item.strip()
                if not import_item:
                    continue
                if import_item.endswith(".css"):
                    continue
                if import_item.startswith("http://") or \
                   import_item.startswith("https://"):
                    continue
                if self.is_compass_enabled and (
                    import_item in ("compass", "compass.scss") or
                    import_item.startswith("compass/")
                ):
                    # Ignore compass imports if Compass is enabled.
                    continue
                imports.add(import_item)
        return sorted(imports)

    def get_full_source_path(self, source_path):
        try:
            return super(SCSS, self).get_full_source_path(source_path)
        except ValueError:
            # Try to locate the source file in directories specified in `load_paths`
            norm_source_path = utils.normalize_path(source_path.lstrip("/"))
            for dirname in self.load_paths:
                full_path = os.path.join(dirname, norm_source_path)
                if os.path.exists(full_path):
                    return full_path
            raise

    def locate_imported_file(self, source_dir, import_path):
        """ Locate the imported file in the source directory.
            Return the path to the imported file relative to STATIC_ROOT

        :param source_dir: source directory
        :type source_dir: str
        :param import_path: path to the imported file
        :type import_path: str
        :returns: str

        """
        import_filename = posixpath.basename(import_path)
        import_dirname = posixpath.dirname(import_path)
        import_filename_root, import_filename_extension = posixpath.splitext(import_filename)

        if import_filename_extension:
            filenames_to_try = [import_filename]
        else:
            # No extension is specified for the imported file, try all supported extensions
            filenames_to_try = [import_filename_root + "." + extension for extension in self.import_extensions]

        if not import_filename.startswith("_"):
            # Try the files with "_" prefix
            filenames_to_try += ["_" + filename for filename in filenames_to_try]

        # Try to locate the file in the directory relative to `source_dir`
        for filename in filenames_to_try:
            source_path = posixpath.normpath(posixpath.join(source_dir, import_dirname, filename))
            try:
                self.get_full_source_path(source_path)
                return source_path
            except ValueError:
                pass

        # Try to locate the file in the directories listed in `load_paths`
        for dirname in self.load_paths:
            for filename in filenames_to_try:
                source_path = posixpath.join(import_dirname, filename)
                if os.path.exists(os.path.join(dirname, utils.normalize_path(source_path))):
                    return source_path

        raise exceptions.StaticCompilationError("Can't locate the imported file: {0}".format(import_path))

    def find_dependencies(self, source_path):
        source = self.get_source(source_path)
        source_dir = posixpath.dirname(source_path)
        dependencies = set()
        for import_path in self.find_imports(source):
            import_path = self.locate_imported_file(source_dir, import_path)
            dependencies.add(import_path)
            dependencies.update(self.find_dependencies(import_path))
        return sorted(dependencies)


# noinspection PyAbstractClass
class SASS(SCSS):

    name = "sass"
    input_extension = "sass"
    import_extensions = ("sass", "scss")

    IMPORT_RE = re.compile(r"@import\s+(.+?)\s*(?:\n|$)")

    def compile_source(self, source):
        args = [
            self.executable,
            "-s",
        ] + self.get_extra_args()
        if self.executable.endswith("scss"):
            args.append("--sass")

        return_code, out, errors = utils.run_command(args, source)
        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out
