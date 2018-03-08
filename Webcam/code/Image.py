
import subprocess
import shlex 
from pathlib import Path

from . import Manifest
from .CustomLogging import Log

class Image:
    """Track data and progress of an image as an object.
    """

    def __init__(self, args, path):
        self.path = path
        self.args = args
        self.log = Log()
        self.current_location = None
        self.manifest = None
        self.captured = False
        self.writen = False
        self.copied = False

    def spawn_manifest(self):
        self.manifest = Manifest(self)

    def queue_copy(self):
        local_file = Path(self.args.ram_disk, self.path.name)
        remote_path = Path(self.args.remote_path, self.path)
        cmd = f"ssh bigbox 'mkdirs -p {remote_path.parent}';scp {local_file} {self.args.remote_host}:{remote_path}"
        self.log.debug(cmd)
        # self.process = subprocess.Popen(shlex.split(cmd))

    def is_copied(self):
        pass