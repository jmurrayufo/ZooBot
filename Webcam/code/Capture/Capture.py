
import shlex
import subprocess

from ..CustomLogging import Log


class Capture:
    # streamer -f jpeg -s1920x1080 -o image.jpeg

    def __init__(self ):
        self.log = Log()
        pass

    def run(self, file_name, size="1920x1080", quality=75):
        self.log.debug(f"Run with filename {file_name}")
        self.log.debug(f"Check if {file_name.parent} exists")
        pass