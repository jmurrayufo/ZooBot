#!/usr/bin/env python3

from pathlib import Path
import argparse
import datetime
import json
import os
import shlex
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

parser.add_argument('--fps',
                    default=30,
                    help="FPS of output video files")

parser.add_argument('--now',
                    action='store_true',
                    help="Process files now")

args = parser.parse_args()
today = datetime.date.today()
movie_process = None
log = Log("VideoProc.py", args)

log.info("Started")

next_scan = datetime.datetime.now()
if args.now:
    log.info("Processing queue right away")
else:
    log.info("Processing will start at the next 1AM")
    next_scan += datetime.timedelta(days=1)
    next_scan = next_scan.replace(hour=23, minute=0, second=0, microsecond=0)


while 1:
    # Scan for new directories without a manifest.json file

    now = datetime.datetime.now()
    if now < next_scan:
        dt = (next_scan-now).total_seconds()
        log.info(f"Sleep for {dt:,.0f} seconds until {next_scan}")
        time.sleep(dt)
        log.info(f"Sleep completed.")

    next_scan = datetime.datetime.now()
    next_scan += datetime.timedelta(days=1)
    next_scan = next_scan.replace(hour=23, minute=0, second=0, microsecond=0)
    log.info(f"Begin process loop")

    glob = list(Path(args.images).glob('**'))
    number_folders = len(glob)

    targets = []

    for folder in glob:
        # Is there a JSON here?
        log.info(f"Scan: {folder}")
        if list(folder.glob("*manifest.json")):
            log.info("Found manifest file!")
            targets.append(Video(folder, args))
            continue

        if list(folder.glob("*.jpeg")):
            log.info("Found jpeg without manifest file!")
            targets.append(Video(folder, args))
            continue

    log.info("Load targets")
    for video in targets:
        video.load()

    targets = [x for x in targets if x.ready]

    log.debug(f"Files before delete: {len(targets)}")

    ffmpeg_processes = []
    for video in targets:
        if video.processed and video.delete_on < datetime.datetime.now():
            log.info(f"{video} is aleady finished processing! Delete?")
            video.delete()
            continue
        elif video.processed:
            log.info(f"{video} is aleady finished processing!")
            continue
        ffmpeg_processes.append(video)

    ffmpeg_processes = [x for x in ffmpeg_processes if not x.deleted]

    log.debug(f"Files after delete: {len(ffmpeg_processes)}")

    log.info("Begin processing loop")

    while len(ffmpeg_processes):
        log.info(f"Processing more files {len(ffmpeg_processes)}")

        video = ffmpeg_processes[0]
        video.start()
        log.info(f"{video} Processing has started.")
        while video.is_running():
            time.sleep(1)
        video.finished()
        log.info(f"{video} is completed.")

        ffmpeg_processes = [x for x in ffmpeg_processes if not x.processed]
