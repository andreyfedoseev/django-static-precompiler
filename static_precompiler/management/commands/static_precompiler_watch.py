from django.contrib.staticfiles.finders import get_finders
from django.core.files.storage import FileSystemStorage
from django.core.management.base import NoArgsCommand
from optparse import make_option
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.settings import STATIC_ROOT
from static_precompiler.utils import get_compilers
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os
import time


def get_watched_dirs():
    dirs = set([STATIC_ROOT])
    for finder in get_finders():
        if hasattr(finder, "storages"):
            for storage in finder.storages.values():
                if isinstance(storage, FileSystemStorage):
                    dirs.add(storage.location)
    return sorted(dirs)


class EventHandler(FileSystemEventHandler):

    def __init__(self, watched_dir, verbosity, compilers):
        self.watched_dir = watched_dir
        self.verbosity = verbosity
        self.compilers = compilers
        super(EventHandler, self).__init__()

    def on_any_event(self, e):
        if e.is_directory or e.event_type not in ("created", "modified"):
            return
        path = e.src_path[len(self.watched_dir):]
        if path.startswith("/"):
            path = path[1:]
        for compiler in self.compilers:
            if compiler.is_supported(path):
                if self.verbosity > 1:
                    if e.event_type == "created":
                        print("Created: '{0}'".format(path))
                    else:
                        print("Modified: '{0}'".format(path))
                try:
                    compiler.handle_changed_file(path)
                except (StaticCompilationError, ValueError) as e:
                    print(e)
                break


class Command(NoArgsCommand):

    help = 'Watch for static files changes and re-compile them if necessary.'

    requires_model_validation = False

    option_list = NoArgsCommand.option_list + (
        make_option("--no-initial-scan",
                    action="store_false",
                    dest="initial_scan",
                    default=True,
                    help="Skip the initial scan of watched directories."),
    )

    def handle_noargs(self, **options):

        watched_dirs = get_watched_dirs()

        print("Watching directories:")
        for watched_dir in watched_dirs:
            print(watched_dir)
        print("\nPress Control+C to exit.\n")

        verbosity = int(options["verbosity"])

        compilers = get_compilers()

        if options["initial_scan"]:
            # Scan the watched directories and compile everything
            for watched_dir in watched_dirs:
                for dirname, dirnames, filenames in os.walk(watched_dir):
                    for filename in filenames:
                        path = os.path.join(dirname, filename)[len(watched_dir):]
                        if path.startswith("/"):
                            path = path[1:]
                        for compiler in compilers:
                            if compiler.is_supported(path):
                                try:
                                    compiler.handle_changed_file(path)
                                except (StaticCompilationError, ValueError) as e:
                                    print(e)
                                break

        observer = Observer()

        for watched_dir in watched_dirs:
            handler = EventHandler(watched_dir, verbosity, compilers)
            observer.schedule(handler, path=watched_dir, recursive=True)

        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
