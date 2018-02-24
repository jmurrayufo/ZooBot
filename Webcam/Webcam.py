#!/usr/bin/env python3

import argparse

from code.CustomLogging import Log
from __version__ import __version__
from code.Mount import Mount



parser = argparse.ArgumentParser(description='Webcam Application')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--fps', 
                    type=float,
                    default=1.0,
                    help='Frames per second')

args = parser.parse_args()


log = Log(args)

log.info("Booting Webcam.py")
log.info(args)

x = Mount()
x.is_mounted()