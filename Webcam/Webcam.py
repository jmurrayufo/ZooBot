#!/usr/bin/env python3.6

import argparse
import datetime
import pathlib
import time


from __version__ import __version__
from code.Capture import Capture
from code.CustomLogging import Log
from code.Mount import Mount
from code import Director

parser = argparse.ArgumentParser(description='Webcam Application')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--frame-delay', 
                    type=float,
                    default=10,
                    help='Delay between frames in seconds')

parser.add_argument('--mount-location',
                    default="/home/jmurray/ZFS",
                    help='Location to attempt to mount')

parser.add_argument('--ram-disk',
                    default="/mnt/ramdisk",
                    help='Location of ramdisk')

parser.add_argument('--remote-host',
                    default="192.168.1.2",
                    help='Location of ramdisk')

parser.add_argument('--remote-dropbox',
                    default="/ZFS/Media/Webcams/Dropbox",
                    help='Remote location with Working and Inbox directories')

parser.add_argument('--director',
                    default=False,
                    action='store_true',
                    help='Use director mode')

args = parser.parse_args()

log = Log(args)

log.info("Booting Webcam.py")
log.info(args)

if args.director:
    log.info("Booting with director mode")
    director = Director(args)
    director.run()
    log.info("Director mode exiting")
    exit()


log.info("Begin main loop")

cpt = Capture(args)
next_capture = datetime.datetime.now()


while 1:

    loop = 0
    now = datetime.datetime.now()
    while next_capture < now:
        next_capture += datetime.timedelta(seconds = args.frame_delay)
        dt = (next_capture - now).total_seconds()
        loop += 1

    if loop > 1: 
        log.warning(f"Cannot keep up! Currently {loop*args.frame_delay:.0f}s behind!")

    time.sleep(dt)


    file_name = now.strftime(f"{args.mount_location}/Webcams/Dragonhab/Cache/%Y/%m/%d/%H_%M_%S.jpeg")

    path = pathlib.Path(file_name)

    cpt.run(path)


log.info("Fin")
