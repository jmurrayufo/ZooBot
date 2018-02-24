#!/usr/bin/env python3.6

import argparse
import datetime
import pathlib
import time

import pygame
import pygame.camera

from __version__ import __version__
from code.Capture import Capture
from code.CustomLogging import Log
from code.Mount import Mount
from code.Camera import Camera




parser = argparse.ArgumentParser(description='Webcam Application')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--frame-delay', 
                    type=float,
                    default=60,
                    help='Delay between frames in seconds')

args = parser.parse_args()

log = Log(args)

log.info("Booting Webcam.py")
log.info(args)

x = Mount()
mount_loc = "/home/jmurray/ZFS"
if not x.is_mounted(mount_loc):
    log.info(f"Didn't find {mount_loc} to be mounted. Fixing that.")
    x.mount("jmurray@192.168.1.2:/ZFS/Media", mount_loc)
    if not x.is_mounted(mount_loc):
        raise OSError("Couldn't mount, oh no!")
else:
    log.info(f"Found {mount_loc} to be mounted.")

log.info("Begin main loop")

cpt = Capture()
next_capture = datetime.datetime.now()


pygame.camera.init()
pygame.camera.list_cameras() #Camera detected or not
cam = pygame.camera.Camera("/dev/video0",(640,480))
cam.start()

camera = Camera(args,"/dev/video0")
camera.get_settings()
camera.config_manual()
camera.push_settings()
camera.log_settings()

while 1:


    if datetime.datetime.now() < next_capture:
        dt = (next_capture - datetime.datetime.now()).total_seconds()
        time.sleep(dt)
        log.debug(dt)

    next_capture += datetime.timedelta(seconds = args.frame_delay)


    dt = datetime.datetime.now()

    file_name = dt.strftime(f"{mount_loc}/Webcams/Dragonhab/%Y/%m/%d/%H_%M_%S.jpeg")

    path = pathlib.Path(file_name)

    camera.push_settings()
    img = cam.get_image()
    camera.get_settings()

    pygame.image.save(img,str(path))
    # break

    # cpt.run(path)
# cap.release()



log.info("Fin")
