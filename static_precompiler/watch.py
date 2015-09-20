import time

from watchdog import events, observers

from static_precompiler import exceptions, utils


class EventHandler(events.FileSystemEventHandler):

    def __init__(self, scanned_dir, verbosity, compilers):
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
                    compiler.handle_changed_file(path)
                except (exceptions.StaticCompilationError, ValueError) as e:
                    print(e)
                break


def watch_dirs(scanned_dirs, verbosity):
    print("Watching directories:")
    for scanned_dir in scanned_dirs:
        print(scanned_dir)
    print("\nPress Control+C to exit.\n")

    compilers = utils.get_compilers().values()
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
