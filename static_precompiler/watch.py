import time

from typing import *  # noqa
from watchdog import events, observers

from . import exceptions, registry
from .compilers import BaseCompiler  # noqa


class EventHandler(events.FileSystemEventHandler):

    # noinspection PyShadowingNames
    def __init__(self, scanned_dir, verbosity, compilers):
        # type: (str, int, List[BaseCompiler]) -> None
        self.scanned_dir = scanned_dir
        self.verbosity = verbosity
        self.compilers = compilers
        super(EventHandler, self).__init__()

    def on_any_event(self, e):
        if e.is_directory or e.event_type not in ("created", "modified"):
            return
        path = e.src_path[len(self.scanned_dir):]
        if path.startswith("/"):
            path = path[1:]
        for compiler in self.compilers:
            if compiler.is_supported(path):
                if self.verbosity > 1:
                    print("Modified: '{0}'".format(path))
                try:
                    compiler.compile(path, from_management=True, verbosity=self.verbosity)
                    if compiler.supports_dependencies:
                        for dependent in compiler.get_dependents(path):
                            compiler.compile(path, from_management=True, verbosity=self.verbosity)
                            self.compile(dependent, from_management=True, verbosity=self.verbosity)
                except (exceptions.StaticCompilationError, ValueError) as e:
                    print(e)
                break


def watch_dirs(scanned_dirs, verbosity):
    print("Watching directories:")
    for scanned_dir in scanned_dirs:
        print(scanned_dir)
    print("\nPress Control+C to exit.\n")

    compilers = registry.get_compilers().values()
    observer = observers.Observer()

    for scanned_dir in scanned_dirs:
        handler = EventHandler(scanned_dir, verbosity, compilers)
        observer.schedule(handler, path=scanned_dir, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
