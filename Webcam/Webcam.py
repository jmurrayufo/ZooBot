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

args = parser.parse_args()

log = Log(args)

log.info("Booting Webcam.py")
log.info(args)

log.info("Booting with director mode")
director = Director(args)
director.run()
log.info("Director mode exiting")