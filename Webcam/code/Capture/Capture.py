
import os
import shlex
import subprocess
import time
import signal
import pygame
import pygame.camera

from ..CustomLogging import Log
from ..Camera import Camera


class Capture:
    # streamer -f jpeg -s1920x1080 -o image.jpeg

    def __init__(self, args):
        self.log = Log()
        self.log.info("Init")
        self.log.info("Init pygame")
        # pygame.camera.init()
        # pygame.camera.list_cameras() #Camera detected or not

        self.log.info("Init Camera")
        self.camera = Camera(args,"/dev/video0")

        self.log.info("Grab Camera settings")
        self.camera.get_settings()
        self.camera.config_manual()
        self.log.info("Push manual Camera settings")
        self.camera.push_settings()
        self.log.info("Log Camera settings")
        self.camera.log_settings()

        # self.log.info("Cameras listed, bind to /dev/video0")
        # self.cam = pygame.camera.Camera("/dev/video0", (640,480) )

        # self.log.info("Start pygame camera")
        # self.cam.start()


    def run(self, file_name):
        # with DelayedKeyboardInterrupt():
        # self.log.debug(f"Run with filename {file_name}")
        if not file_name.parent.exists():
            self.log.info(f"Creating path {file_name.parent}")
            os.makedirs(file_name.parent)

        # Now capture an image
        t0 = time.time()
        cmd = f"streamer -f jpeg -s 1920x1080 -o {file_name}"
        ps = subprocess.run(shlex.split(cmd), 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)

        # img = self.cam.get_image()
        # pygame.image.save(img, str(file_name))
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