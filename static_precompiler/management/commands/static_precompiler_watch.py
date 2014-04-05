from django.core.management.base import NoArgsCommand
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.settings import STATIC_ROOT
from static_precompiler.utils import get_compilers
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os
import time


class EventHandler(FileSystemEventHandler):

    def __init__(self, verbosity, compilers):
        self.verbosity = verbosity
        self.compilers = compilers
        super(EventHandler, self).__init__()

    def on_any_event(self, e):
        if e.is_directory or e.event_type not in ("created", "modified"):
            return
        path = e.src_path[len(STATIC_ROOT):]
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

    help = 'Watch for file changes in STATIC_ROOT and re-compile them if necessary.'

    requires_model_validation = False

    def handle_noargs(self, **options):

        print("Watching '{0}' for changes.\nPress Control+C to exit.\n".format(STATIC_ROOT))

        verbosity = int(options["verbosity"])

        compilers = get_compilers()

        # Scan the root folder and compile everything
        for dirname, dirnames, filenames in os.walk(STATIC_ROOT):
            for filename in filenames:
                path = os.path.join(dirname, filename)[len(STATIC_ROOT):]
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
        observer.schedule(EventHandler(verbosity, compilers), path=STATIC_ROOT, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
