
import json
from pathlib import Path
from .CustomLogging import Log


class Manifest:
    """Handle image metadata and it's associated file
    """


    def __init__(self, image):
        self.image = image
        self.log = Log()


    def write(self):
        data = {"file_name":self.image.path.name,
                "destination":self.image.path.parent,
                "local_path":self.image.local_path}
        manifest_file = Path(self.image.local_path.parent, self.image.local_path.stem, "json")
        self.log.debug(f"Write to: {manifest_file}")