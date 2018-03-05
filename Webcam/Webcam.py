#!/usr/bin/env python3.6

import argparse
import datetime
import pathlib
import time


from __version__ import __version__
from code.Capture import Capture
from code.CustomLogging import Log
from code.Mount import Mount

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


args = parser.parse_args()

log = Log(args)

log.info("Booting Webcam.py")
log.info(args)


log.info("Begin main loop")

cpt = Capture(args)
next_capture = datetime.datetime.now()


while 1:
    loop = 0
    while datetime.datetime.now() > next_capture:
        loop += 1
        next_capture += datetime.timedelta(seconds = args.frame_delay)
    
    if loop > 1:
        log.warning(f"Cannot keep up! Currently {args.frame_delay*loop}s behind!")


    dt = datetime.datetime.now()

    file_name = dt.strftime(f"{args.mount_location}/Webcams/Dragonhab/%Y/%m/%d/%H_%M_%S.jpeg")

    path = pathlib.Path(file_name)

    cpt.run(path)


log.info("Fin")
