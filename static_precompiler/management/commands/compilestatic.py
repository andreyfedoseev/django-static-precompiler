import os
import sys

from django.contrib.staticfiles.finders import get_finders
from django.core.files.storage import FileSystemStorage
from django.core.management.base import NoArgsCommand
from optparse import make_option
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.settings import STATIC_ROOT
from static_precompiler.utils import get_compilers


def get_scanned_dirs():
    dirs = set([STATIC_ROOT])
    for finder in get_finders():
        if hasattr(finder, "storages"):
            for storage in finder.storages.values():
                if isinstance(storage, FileSystemStorage):
                    dirs.add(storage.location)
    return sorted(dirs)


class Command(NoArgsCommand):

    help = "Compile static files."

    requires_model_validation = False

    option_list = NoArgsCommand.option_list + (
        make_option("--watch",
                    action="store_true",
                    dest="watch",
                    default=False,
                    help="Watch for changes and recompile if necessary."),
        make_option("--no-initial-scan",
                    action="store_false",
                    dest="initial_scan",
                    default=True,
                    help="Skip the initial scan of watched directories in --watch mode."),
    )

    def handle_noargs(self, **options):

        if not options["watch"] and not options["initial_scan"]:
            sys.exit("--no-initial-scan option should be used with --watch.")

        scanned_dirs = get_scanned_dirs()

        verbosity = int(options["verbosity"])

        compilers = get_compilers().values()

        if not options["watch"] or options["initial_scan"]:
            # Scan the watched directories and compile everything
            for scanned_dir in scanned_dirs:
                for dirname, dirnames, filenames in os.walk(scanned_dir):
                    for filename in filenames:
                        path = os.path.join(dirname, filename)[len(scanned_dir):]
                        if path.startswith("/"):
                            path = path[1:]
                        for compiler in compilers:
                            if compiler.is_supported(path):
                                try:
                                    compiler.handle_changed_file(path)
                                except (StaticCompilationError, ValueError) as e:
                                    print(e)
                                break

        if options["watch"]:
            from static_precompiler.watch import watch_dirs
            watch_dirs(scanned_dirs, verbosity)
