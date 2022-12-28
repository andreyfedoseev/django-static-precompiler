import os
import sys
from argparse import ArgumentParser
from typing import Any, Iterable, List

import django
import django.contrib.staticfiles.finders
import django.core.files.storage
import django.core.management.base

from ... import exceptions, registry, settings, utils
from ...types import StrCollection


def get_scanned_dirs() -> List[str]:
    dirs = set()
    if settings.STATIC_ROOT:
        dirs.add(settings.STATIC_ROOT)
    for finder in django.contrib.staticfiles.finders.get_finders():
        if isinstance(
            finder,
            (
                django.contrib.staticfiles.finders.FileSystemFinder,
                django.contrib.staticfiles.finders.AppDirectoriesFinder,
            ),
        ):
            for storage in finder.storages.values():
                if isinstance(storage, django.core.files.storage.FileSystemStorage):
                    dirs.add(storage.location)
    return sorted(dirs)


def list_files(scanned_dirs: StrCollection) -> Iterable[str]:
    for scanned_dir in scanned_dirs:
        for dirname, _dirnames, filenames in os.walk(scanned_dir):
            for filename in filenames:
                path = os.path.join(dirname, filename)[len(scanned_dir) :]
                if path.startswith("/"):
                    path = path[1:]
                yield path


def delete_stale_files(compiled_files: StrCollection) -> None:
    compiled_files = {
        os.path.join(settings.ROOT, utils.normalize_path(compiled_file)) for compiled_file in compiled_files
    }
    actual_files = set()
    for dirname, _dirnames, filenames in os.walk(os.path.join(settings.ROOT, settings.OUTPUT_DIR)):
        for filename in filenames:
            actual_files.add(os.path.join(dirname, filename))
    stale_files = actual_files - compiled_files
    for stale_file in stale_files:
        os.remove(stale_file)


class Command(django.core.management.base.BaseCommand):

    help = "Compile static files."

    requires_system_checks = []  # type: ignore

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--ignore-dependencies",
            action="store_true",
            dest="ignore_dependencies",
            default=False,
            help="Disable dependency tracking, this prevents any database access.",
        )
        parser.add_argument(
            "--delete-stale-files",
            action="store_true",
            dest="delete_stale_files",
            default=False,
            help="Delete compiled files don't have matching source files.",
        )
        parser.add_argument(
            "--watch",
            action="store_true",
            dest="watch",
            default=False,
            help="Watch for changes and recompile if necessary.",
        )
        parser.add_argument(
            "--no-initial-scan",
            action="store_false",
            dest="initial_scan",
            default=True,
            help="Skip the initial scan of watched directories in --watch mode.",
        )

    def handle(self, *args: Any, **options: Any) -> None:

        if not options["watch"] and not options["initial_scan"]:
            sys.exit("--no-initial-scan option should be used with --watch.")

        scanned_dirs = get_scanned_dirs()
        verbosity = int(options["verbosity"])
        compilers = registry.get_compilers().values()

        if options["ignore_dependencies"]:
            for compiler in compilers:
                compiler.supports_dependencies = False

        if not options["watch"] or options["initial_scan"]:
            # Scan the watched directories and compile everything
            compiled_files = set()
            for path in sorted(set(list_files(scanned_dirs))):
                for compiler in compilers:
                    if compiler.is_supported(path):
                        break
                else:
                    continue

                try:
                    compiled_files.add(compiler.compile(path, from_management=True, verbosity=verbosity))
                except (exceptions.StaticCompilationError, ValueError) as e:
                    print(e)

            if options["delete_stale_files"]:
                delete_stale_files(list(compiled_files))

        if options["watch"]:
            from static_precompiler.watch import watch_dirs

            watch_dirs(scanned_dirs, verbosity)


if django.VERSION < (3, 2):
    Command.requires_system_checks = False  # type: ignore
