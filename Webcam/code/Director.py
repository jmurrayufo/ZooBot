
import datetime
import pathlib
import time
import numpy as np

from .Ramdisk import Ramdisk
from .Camera import Camera
from .CustomLogging import Log

class Director:
    """ Oversee the rest of the application in runtime
    """

    def __init__(self, args):
        self.log = Log()
        self.log.info("Begin Director Init")
        self.args = args
        self.ramdisk = Ramdisk(self.args.ram_disk)
        self.camera = Camera(args)
        self.log.info("Completed Director Init")


    def run(self):
        base_wait = 1
        copy_queue = []
        cleanup_queue = []
        move_queue = []
        while 1:
            # Determine if we need to throttle back
            fill_percent = self.ramdisk.fill_percent()
            dt = base_wait*np.exp(fill_percent*5) - 1.0

            # Wait perscribed time
            self.log.debug(f"Sleep for: {dt}")
            time.sleep(dt)

            # Capture image
            now = datetime.datetime.now()
            file_name = now.strftime(f"Dragonhab/%Y/%m/%d/%H_%M_%S.jpeg")
            path = pathlib.Path(file_name)
            image = self.camera.capture(path)

            # Write image and manifest to Ramdisk
            image.spawn_manifest()

            # Queue up for SCP to bigbox
            image.queue_copy()
            copy_queue.append(image)

            # Check for copied files to move
            for image in copy_queue:
                if image.is_copied():
                    image.move_results()
                    move_queue.append(image)
            copy_queue = [x for x in copy_queue if x not in move_queue]

            # Check for copied files to delete
            for image in move_queue:
                if image.is_copied():
                    image.cleanup()
                    cleanup_queue.append(image)
            move_queue = [x for x in move_queue if x not in cleanup_queue]

            cleanup_queue = [x for x in cleanup_queue if not x.is_cleaned()]



            # break # TODO: Remove this!
