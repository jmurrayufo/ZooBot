
import subprocess
import shlex 
from pathlib import Path

from .Manifest import Manifest
from .CustomLogging import Log

class Image:
    """Track data and progress of an image as an object.
    """

    def __init__(self, args, path, annotate_text):
        self.annotate_text = annotate_text
        self.args = args
        self.path = path

        self.local_path = Path(self.args.ram_disk, self.path.name)

        self.log = Log()
        self.current_location = None
        self.manifest = None
        self.captured = False
        self.writen = False
        self.copied = False

    def spawn_manifest(self):
        self.manifest = Manifest(self)

    def queue_copy(self):

        if not self.manifest:
            self.spawn_manifest()

        # self.remote_dropbox = Path(self.args.remote_dropbox, self.path)

        cmd = f"scp {self.local_path} {self.args.remote_host}:{self.args.remote_dropbox}/Working/"
        self.log.debug(cmd)

        self.manifest.write()

        cmd = f"scp {self.manifest.get_file()} {self.args.remote_host}:{self.args.remote_dropbox}/Working/"
        self.log.debug(cmd)

        cmd = f"ssh bigbox 'mv {self.args.remote_dropbox}/Working/{self.manifest.get_file()} {self.args.remote_dropbox}/Working/{self.path.name} {self.args.remote_dropbox}/Inbox/'"
        self.log.debug(cmd)
        # self.process = subprocess.Popen(shlex.split(cmd))

    def is_copied(self):
        pass