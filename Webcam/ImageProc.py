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
from code.MDFive import MDFive

parser = argparse.ArgumentParser(description='Webcam Application')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--scan-rate', 
                    type=float,
                    default=10,
                    help='Delay between Inbox scans')

parser.add_argument('--inbox-location',
                    default="/ZFS/Media/Webcams/Dropbox/Inbox/",
                    help='Location to scan')

parser.add_argument('--error-location',
                    default="/ZFS/Media/Webcams/Dropbox/Error/",
                    help='Location of error files')

parser.add_argument('--webcam-base-location',
                    default="/ZFS/Media/Webcams/",
                    help='Location to scan')

parser.add_argument('--web-image-location',
                    default="/ZFS/Media/Webcams/Dragonhab/fanghur.jpeg",
                    help='Location to scan')

args = parser.parse_args()
today = datetime.date.today()
movie_process = None
args.web_image_location = Path(args.web_image_location)
log = Log("ImageProc.py",args)

log.info("Started")

next_scan = datetime.datetime.now()
while 1:
    while datetime.datetime.now() < next_scan:
        time.sleep(0.1)

    next_scan += datetime.timedelta(seconds=args.scan_rate)
    # Make sure we have a folder to write too!

    glob = list(Path(args.inbox_location).glob('*.json'))
    number_jsons = len(glob)

    if number_jsons > 5:
        log.warning(f"Excessive images found ({number_jsons:,d})")

    for json_file in glob:
        if datetime.datetime.now() > next_scan:
            log.warning("Didn't finish scan in time.")
            break
        with open(json_file,'r') as fp:
            data = json.load(fp)
        image_file = Path(args.inbox_location,data['file_name'])

        if not image_file.exists():
            log.error(f"File {json_file} had no image file!")
            shutuil.move(json_file, args.error_location)
            continue

        image_hash = MDFive(image_file).checksum()

        # TODO: Handle errors here
        if image_hash != data['md5']:
            log.error(f"Checksum mismatch in {json_file}")
            shutil.move(json_file, args.error_location)
            shutil.move(image_file, args.error_location)
            continue

        destination_path = Path(args.webcam_base_location, data['destination'])
        os.makedirs(destination_path, exist_ok=True)
        cmd = f"jpegoptim {image_file} -p -f -d {destination_path}"
        subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE).wait()

        # Handle errors
        output = Path(destination_path, data['file_name'])
        if not output.exists():
            log.error(f"File not seen after compression, {output} does not exist. {data['file_name']} moved to error")
            shutil.move(json_file, args.error_location)
            shutil.move(image_file, args.error_location)
            continue

        # Compress for softlink viewing
        cmd = f"jpegoptim {image_file} -S 300 -d {str(args.web_image_location.parent)}"
        subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE).wait()

        shutil.move(Path(args.web_image_location.parent, data['file_name']), Path(args.web_image_location.parent,"fanghur.jpeg"))


        os.remove(json_file)
        os.remove(image_file)


"""

2018-04-23 10:04:33,979 ERROR ImageProc.py:74 File /ZFS/Media/Webcams/Dropbox/Inbox/10_04_19.json had no image file!
Traceback (most recent call last):
      File "./ImageProc.py", line 75, in <module>
          shutuil.move(json_file, args.error_location)
          NameError: name 'shutuil' is not defined
          You have new mail in /var/mail/jmurray
"""
