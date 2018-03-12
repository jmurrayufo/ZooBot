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
from code.MDFive import MDFive

parser = argparse.ArgumentParser(description='Webcam Application')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--scan-rate', 
                    type=float,
                    default=60,
                    help='Delay between Inbox scans')

parser.add_argument('--inbox-location',
                    default="/ZFS/Media/Webcams/Dropbox/Inbox/",
                    help='Location to scan')

parser.add_argument('--webcam-base-location',
                    default="/ZFS/Media/Webcams/",
                    help='Location to scan')

args = parser.parse_args()

log = Log(args)

next_scan = datetime.datetime.now()

while 1:
    while datetime.datetime.now() < next_scan:
        time.sleep(1)

    # Make sure we have a folder to write too!

    glob = Path(args.inbox_location).glob('*.json')
    for file in glob:
        with open(file,'r') as fp:
            data = json.load(fp)
        image_path = Path(args.inbox_location,data['file_name'])
        image_hash = MDFive(image_path).checksum()

        # TODO: Handle errors here
        if image_hash != data['md5']:
            self.log.error(f"Checksum mismatch in {file}")

        destination_path = Path(args.webcam_base_location, data['destination'])
        os.makedirs(destination_path, exist_ok=True)
        cmd = f"jpegoptim {image_path} -p -f -d {destination_path}"
        subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE).wait()
        os.remove(file)
        os.remove(image_path)

    next_scan += datetime.timedelta(seconds=args.scan_rate)
