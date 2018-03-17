
from pathlib import Path
import re
import json

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


    def load(self):

        manifest_file = list(self.target_folder.glob("*manifest.json"))
        if manifest_file:
            with open(manifest_file[0],'r') as fp:
                self.__dict__.update(json.load(fp))
                self.target_folder = Path(self.target_folder)
                self.output_file = Path(self.output_file)
                self.manifest_file = Path(self.manifest_file)

        else:
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
                json.dump(data, fp)


# class CustomEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, PosixPath):
#             return str(obj)
#         # Let the base class default method raise the TypeError
#         return json.JSONEncoder.default(self, obj)