#!/usr/bin/env python3

import argparse

from code.CustomLogging import Log
from __version__ import __version__



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