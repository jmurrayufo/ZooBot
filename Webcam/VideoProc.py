#!/usr/bin/env python3

from pathlib import Path
import argparse
import datetime
import json
import os
import shlex
import shutil
import subprocess
import time

from __version__ import __version__
from code.CustomLogging import Log
from code.Video import Video

parser = argparse.ArgumentParser(description='Video Post Processor')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--images',
                    default="/ZFS/Media/Webcams/Dragonhab/Cache",
                    help='Scan for image folders under this directory')

parser.add_argument('--videos',
                    default="/ZFS/Media/Webcams/Dragonhab/Videos",
                    help='Output directory of videos')

args = parser.parse_args()
today = datetime.date.today()
movie_process = None
log = Log("VideoProc.py", args)

log.info("Started")

next_scan = datetime.datetime.now()

while 1:
    # Scan for new directories without a manifest.json file

    now = datetime.datetime.now()
    if now < next_scan:
        dt = (next_scan-now).total_seconds()
        log.info(f"Sleep for {dt:,.0f} seconds")
        time.sleep(dt)

    next_scan = datetime.datetime.now()
    next_scan += datetime.timedelta(days=1)
    next_scan = next_scan.replace(hour=1, minute=0, second=0, microsecond=0)
    log.info(f"Wakeup and begin process loop")

    glob = list(Path(args.images).glob('**'))
    number_folders = len(glob)

    targets = []

    for folder in glob:
        # Is there a JSON here?
        log.info(f"Scan: {folder}")
        if list(folder.glob("*manifest.json")):
            log.debug("Found manifest file!")
            targets.append(Video(folder, args))
            continue

        if list(folder.glob("*.jpeg")):
            log.debug("Found jpeg without manifest file!")
            targets.append(Video(folder, args))
            break
            continue

    for video in targets:
        video.load()
        # log.debug(video.__dict__)

    break