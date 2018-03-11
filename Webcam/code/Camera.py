
from picamera import PiCamera
import datetime
import os
import signal
import time
from pathlib import Path

from .CustomLogging import Log
from .Image import Image


class Camera:

    def __init__(self, args):
        self.args = args
        self.log = Log()
        self.log.info("Init")
        self.log.info("Init PiCamera")
        self.camera = PiCamera()
        self.log.info(f"Booted with a camera of {self.camera.revision}")
        self.camera.resolution = (2592,1944)
        # self.camera.resolution = (1920,1080)
        self.camera.framerate = 1
        self.camera.iso = 400
        self.log.info("Camera configured, sleeping...")
        time.sleep(2)
        self.log.info("Camera stable, finish setup")
        self.camera.rotation = 0
        self.camera.shutter_speed = 15000
        self.log.info(f"Shutter Speed: {self.camera.shutter_speed}")
        # self.camera.exposure_amode = 'off'
        # g = self.camera.awb_gains
        # self.log.info(f"AWB gains: {g}")
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = (1.5, 1.2)
        self.log.info("Camera setup completed!")
        self.annotate_text = ""


    def capture(self, file_name):

        # Now capture an image
        t0 = datetime.datetime.now()

        self.camera.annotate_text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        path = Path(self.args.ram_disk, file_name.name)
        
        self.camera.capture(str(path))

        # self.log.debug(datetime.datetime.now()-t0)
        return Image(self.args, file_name, self.camera.annotate_text)

