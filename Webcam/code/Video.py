
from pathlib import Path
import json
import re
import time
import subprocess
import shlex

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


    def __repr__(self):
        return f"Video({self.target_folder})"


    def load(self):

        manifest_file = list(self.target_folder.glob("*manifest.json"))
        if manifest_file:
            try: 
                with open(manifest_file[0],'r') as fp:
                    self.__dict__.update(json.load(fp))
                    self.target_folder = Path(self.target_folder)
                    self.output_file = Path(self.output_file)
                    self.manifest_file = Path(self.manifest_file)
                    return
            except json.decoder.JSONDecodeError:
                self.log.exception("JSON was corrupted somehow, creating a new one")


        self.log.info("No manifest found, generate one now!")

        match_obj = re.search("(\d{4})/(\d{2})/(\d{2})", str(self.target_folder))
        year, month, day = match_obj.groups()
        self.output_file = Path(self.args.videos, f"{year}_{month}_{day}.mp4")
        self.manifest_file = Path(self.target_folder, f"{year}_{month}_{day}_manifest.json")

        data = dict(self.__dict__)
        del data['log']
        del data['args']
        data['target_folder'] = str(data['target_folder'])
        data['output_file'] = str(data['output_file'])
        data['manifest_file'] = str(data['manifest_file'])

        with open(self.manifest_file,'w') as fp:
            json.dump(data, fp, indent=2)

    def start(self):
        if self.process is not None:
            # Check to see if we are done, mark this as done, and return
            self.log.critical("Process already started!")
            return

        # Check to see if we are old enough (min 1 hours)
        # Loop through all JPEGs 
        for image in self.target_folder.glob("*.jpeg"):
            if time.time() - image.stat().st_mtime < 1*60*60:
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

        data = dict(self.__dict__)
        del data['log']
        del data['args']
        data['target_folder'] = str(data['target_folder'])
        data['output_file'] = str(data['output_file'])
        data['manifest_file'] = str(data['manifest_file'])

        with open(self.manifest_file,'w') as fp:
            json.dump(data, fp, indent=2)


# class CustomEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, PosixPath):
#             return str(obj)
#         # Let the base class default method raise the TypeError
#         return json.JSONEncoder.default(self, obj)