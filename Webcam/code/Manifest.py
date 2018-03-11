
from pathlib import Path, PosixPath
import json
import os

from .CustomLogging import Log
from .MDFive import MDFive


class Manifest:
    """Handle image metadata and it's associated file
    """


    def __init__(self, image):
        self.image = image
        self.manifest_file = None
        self.log = Log()


    def write(self):
        md5 = MDFive(self.image.local_path).checksum()
        data = {"file_name":self.image.path.name,
                "destination":self.image.path,
                "local_path":self.image.local_path,
                "st_size": self.image.stat.st_size,
                "st_atime": self.image.stat.st_atime,
                "st_mtime": self.image.stat.st_mtime,
                "st_ctime": self.image.stat.st_ctime,
                "md5":md5,
                }
        self.manifest_file = Path(self.image.local_path.parent, self.image.local_path.stem + ".json")
        with open(self.manifest_file,'w') as fp:
            json.dump(data, fp, indent=2, cls=CustomEncoder)


    def get_file(self):
        return self.manifest_file


    def cleanup(self):
        os.remove(self.manifest_file)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PosixPath):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)