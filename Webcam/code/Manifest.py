
import json
from pathlib import Path, PosixPath
from .CustomLogging import Log


class Manifest:
    """Handle image metadata and it's associated file
    """


    def __init__(self, image):
        self.image = image
        self.manifest_file = None
        self.log = Log()


    def write(self):
        data = {"file_name":self.image.path.name,
                "destination":self.image.path,
                "local_path":self.image.local_path}
        self.manifest_file = Path(self.image.local_path.parent, self.image.local_path.stem + ".json")
        self.log.debug(f"Write to: {self.manifest_file}")
        self.log.debug(json.dumps(data, cls=CustomEncoder))


    def get_file(self):
        return self.manifest_file


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PosixPath):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)