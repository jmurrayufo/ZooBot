
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
        self.log.debug(f"Run with filename {file_name}")
        if not file_name.parent.exists():
            self.log.info(f"Creating path {file_name.parent}")
            os.makedirs(file_name.parent)

        # Now capture an image
        cmd = f"streamer -f jpeg -s1920x1080 -o {file_name}"
        t0 = time.time()
        with DelayedKeyboardInterrupt():
            ps = subprocess.run(shlex.split(cmd), 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        t1 = time.time()
        self.log.debug(f"Capture took {t1-t0}s. Max framerate is {1/(t1-t0)}fps")



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