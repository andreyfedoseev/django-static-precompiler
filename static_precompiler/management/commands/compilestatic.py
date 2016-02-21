import optparse
import os
import sys

import django.contrib.staticfiles.finders
import django.core.files.storage
import django.core.management.base

from static_precompiler import exceptions, settings, utils


def get_scanned_dirs():
    dirs = set()
    if settings.STATIC_ROOT:
        dirs.add(settings.STATIC_ROOT)
    for finder in django.contrib.staticfiles.finders.get_finders():
        if hasattr(finder, "storages"):
            for storage in finder.storages.values():
                if isinstance(storage, django.core.files.storage.FileSystemStorage):
                    dirs.add(storage.location)
    return sorted(dirs)


class Command(django.core.management.base.NoArgsCommand):

    help = "Compile static files."

    requires_model_validation = False

    option_list = django.core.management.base.NoArgsCommand.option_list + (
        optparse.make_option("--watch",
                             action="store_true",
                             dest="watch",
                             default=False,
                             help="Watch for changes and recompile if necessary."),
        optparse.make_option("--no-initial-scan",
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

        compilers = utils.get_compilers().values()

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
                                    compiler.handle_changed_file(path, verbosity=options["verbosity"])
                                except (exceptions.StaticCompilationError, ValueError) as e:
                                    print(e)
                                break

        if options["watch"]:
            from static_precompiler.watch import watch_dirs
            watch_dirs(scanned_dirs, verbosity)
