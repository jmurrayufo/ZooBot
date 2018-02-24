
import shlex
import subprocess
import os

from ..CustomLogging import Log


class Capture:
    # streamer -f jpeg -s1920x1080 -o image.jpeg

    def __init__(self ):
        self.log = Log()
        pass

    def run(self, file_name, size="1920x1080", quality=75):
        self.log.debug(f"Run with filename {file_name}")
        if not file_name.parent.exists():
            self.log.info(f"Creating path {file_name.parent}")
            os.makedirs(file_name.parent)
        pass