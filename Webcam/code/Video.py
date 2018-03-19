
from pathlib import Path
import datetime
import json
import re
import shlex
import subprocess
import time

from .CustomLogging import Log

class Video:


    def __init__(self, target_folder, args):
        self.log = Log()

        self.target_folder = target_folder
        self.args = args

        self.images = 0
        self.output_file = None
        self.process = None
        self.processed = False
        self.manifest_file = None
        self.ready = False
        self.w = None
        self.deleted = False


    def __repr__(self):
        return f"Video({self.target_folder})"

    def set_ready_flag(self):
        self.ready = True
        for image in self.target_folder.glob("*.jpeg"):
            if time.time() - image.stat().st_mtime < 1*55*60:
                self.log.info(f"Skipping, {image} is only {time.time() - image.stat().st_mtime}s old")
                self.ready = False
                return

    def load(self):
        manifest_file = list(self.target_folder.glob("*manifest.json"))
        if manifest_file:
            self.log.info("Manifest file found, attempt to load")
            try: 
                with open(manifest_file[0],'r') as fp:
                    self.__dict__.update(json.load(fp))
                self.target_folder = Path(self.target_folder)
                self.output_file = Path(self.output_file)
                self.manifest_file = Path(self.manifest_file)

                if self.delete_on:
                    if type(self.delete_on) in [int,float]:
                        self.log.warning("Old time format detected!")
                        self.delete_on = datetime.datetime.fromtimestamp(self.delete_on)
                    else:
                        self.delete_on = datetime.datetime.strptime(self.delete_on,"%Y-%m-%dT%H:%M:%S")
                    self.log.info(f"{self} marked for deletion on {self.delete_on}")

                self.set_ready_flag()
                return
            except json.decoder.JSONDecodeError:
                self.log.exception("JSON was corrupted somehow, creating a new one")


        self.log.info("No manifest found, generate one now!")
        
        self.set_ready_flag()

        match_obj = re.search("(\d{4})/(\d{2})/(\d{2})", str(self.target_folder))
        year, month, day = match_obj.groups()
        self.output_file = Path(self.args.videos, f"{year}_{month}_{day}.mp4")
        self.manifest_file = Path(self.target_folder, f"{year}_{month}_{day}_manifest.json")

        data = dict(self.__dict__)
        del data['log']
        del data['args']
        # data['target_folder'] = str(data['target_folder'])
        # data['output_file'] = str(data['output_file'])
        # data['manifest_file'] = str(data['manifest_file'])

        with open(self.manifest_file,'w') as fp:
            json.dump(data, fp, indent=2, cls=CustomEncoder)


    def delete(self):
        self.log.info(f"Deleting {self}.")
        # shutil.rmtree(self.target_folder)
        # self.deleted = true


    def start(self):
        if self.process is not None:
            # Check to see if we are done, mark this as done, and return
            self.log.critical("Process already started!")
            return

        # Check to see if we are old enough (min 1 hours)
        # Loop through all JPEGs 
        for image in self.target_folder.glob("*.jpeg"):
            if time.time() - image.stat().st_mtime < 1*55*60:
                self.log.info(f"Skipping, {image} is only {time.time() - image.stat().st_mtime} old")
                return

        # Kickoff process to compress this

        cmd = f"ffmpeg -y -r 30 -pattern_type glob -i '{str(self.target_folder)}/*.jpeg' -r 30 {str(self.output_file)}"
        self.log.debug(cmd)
        self.process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def is_running(self):
        if self.process is None:
            self.log.critical("Cannot update a process that isn't running!")
            return False

        ret = self.process.poll()
        return ret is None


    def finished(self):
        # Mark json as completed, and not needing another update

        self.processed = True
        self.process = None
        self.delete_on = datetime.datetime.now() + datetime.timedelta(days=7) - datetime.timedelta(hours=2)

        data = dict(self.__dict__)
        del data['log']
        del data['args']
        # data['target_folder'] = str(data['target_folder'])
        # data['output_file'] = str(data['output_file'])
        # data['manifest_file'] = str(data['manifest_file'])
        # data['delete_on'] = data['delete_on'].strftime("%Y-%m-%dT%H:%M:%S")

        with open(self.manifest_file,'w') as fp:
            json.dump(data, fp, indent=2, cls=CustomEncoder)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PosixPath):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S")
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)