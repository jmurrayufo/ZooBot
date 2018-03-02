
from picamera import PiCamera
import datetime
import os
import shlex
import signal
import subprocess
import time

from ..CustomLogging import Log
from ..Mount import Mount


class Capture:

    def __init__(self, args):
        self.log = Log()
        self.log.info("Init")
        self.log.info("Init PiCamera")
        self.camera = PiCamera()
        self.log.info(f"Booted with a camera of {self.camera.revision}")
        self.camera.resolution = (2560,1440)
        self.camera.framerate = 1
        self.camera.rotation = 270
        self.log.info("Camera configured, sleeping...")
        time.sleep(2)
        self.log.info("Camera setup completed!")


    def run(self, file_name):
        # with DelayedKeyboardInterrupt():
        if not file_name.parent.exists():
            self.log.info(f"Creating path {file_name.parent}")
            os.makedirs(file_name.parent)


        x = Mount()
        mount_loc = "/home/jmurray/ZFS"
        if not x.is_mounted(mount_loc):
            log.info(f"Didn't find {mount_loc} to be mounted. Fixing that.")
            x.mount("jmurray@192.168.1.2:/ZFS/Media", mount_loc)
            if not x.is_mounted(mount_loc):
                raise OSError("Couldn't mount, oh no!")

        # Now capture an image
        t0 = time.time()
        self.camera.annotate_text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.camera.capture(str(file_name))
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