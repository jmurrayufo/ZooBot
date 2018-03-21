
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
        self.ramdisk.clean()
        self.camera = Camera(args)
        self.log.info("Completed Director Init")
        self.next_capture = datetime.datetime.now()


    def run(self):
        base_wait = 1
        copy_queue = []
        cleanup_queue = []
        move_queue = []
        while 1:

            dawn = datetime.time(hour=6, minute=16, second=0)
            dusk = datetime.time(hour=21, minute=48, second=9)
            now = datetime.datetime.now().time()
            if now < dawn or now > dusk:
                self.log.info(f"Night mode active until {dawn}")
                while now < dawn or now > dusk:
                    time.sleep(10)
                    dawn = datetime.time(hour=6, minute=16, second=0)
                    dusk = datetime.time(hour=21, minute=48, second=9)
                    now = datetime.datetime.now().time()
                self.log.info("Night mode completed, resuming pictures.")



            # Determine if we need to throttle back
            fill_percent = self.ramdisk.fill_percent()
            if fill_percent > 0.95:
                self.log.critical("Ramdisk is above 95%% full! Sleeping until this is fixed!")
                while self.ramdisk.fill_percent() > 0.95:
                    time.sleep(10)
                self.log.critical(f"Ramdisk is now at {self.ramdisk.fill_percent():.1%} full, resuming")
            extra_delay = base_wait*np.exp(fill_percent*5) - 1.0
            if extra_delay > self.args.frame_delay:
                self.log.warning(f"Ramdisk near capacity ({self.ramdisk.fill_percent():%}), delaying extra {extra_delay:.1f} seconds")

            self.next_capture += datetime.timedelta(seconds=extra_delay)
            self.next_capture += datetime.timedelta(seconds=self.args.frame_delay)

            # Wait perscribed time
            if datetime.datetime.now() > self.next_capture:
                self.log.warning(f"Capture is currently {datetime.datetime.now() - self.next_capture} behind")
            else:
                sleep_time = self.next_capture - datetime.datetime.now()
                sleep_time = sleep_time.total_seconds()
                # self.log.debug(f"Sleep for: {sleep_time}")
                time.sleep(sleep_time)


            # Capture image
            now = datetime.datetime.now()
            file_name = now.strftime(f"Dragonhab/Cache/%Y/%m/%d/%H_%M_%S.jpeg")
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
