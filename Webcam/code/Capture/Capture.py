
import os
import shlex
import subprocess
import time
import signal

from ..CustomLogging import Log


class Capture:
    # streamer -f jpeg -s1920x1080 -o image.jpeg

    def __init__(self ):
        self.log = Log()
        pass

    def run(self, file_name, size="1920x1080", quality=75):
        # with DelayedKeyboardInterrupt():
        # self.log.debug(f"Run with filename {file_name}")
        if not file_name.parent.exists():
            self.log.info(f"Creating path {file_name.parent}")
            os.makedirs(file_name.parent)

        # Now capture an image
        cmd = f"streamer -f jpeg -s {size} -o {file_name}"
        t0 = time.time()
        ps = subprocess.run(shlex.split(cmd), 
                            preexec_fn = preexec_function,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
        t1 = time.time()


def preexec_function():
    # Ignore the SIGINT signal by setting the handler to the standard
    # signal handler SIG_IGN.
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class DelayedKeyboardInterrupt(object):
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)
        self.log = Log()

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        self.log.critical('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.log.critical("Now handling SIGINT")
            self.old_handler(*self.signal_received)