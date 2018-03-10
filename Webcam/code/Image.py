
from pathlib import Path
import os
import shlex 
import subprocess

from .Manifest import Manifest
from .CustomLogging import Log

class Image:
    """Track data and progress of an image as an object.
    """

    def __init__(self, args, path, annotate_text):
        self.log = Log()

        self.annotate_text = annotate_text
        self.args = args
        self.path = path
        self.local_path = Path(self.args.ram_disk, self.path.name)

        self.stat = self.local_path.stat()

        self.current_location = None
        self.manifest = None
        self.copied = False
        self.moved = False
        self.cleaned = False


    def spawn_manifest(self):
        self.manifest = Manifest(self)


    def queue_copy(self):

        if not self.manifest:
            self.spawn_manifest()

        # self.remote_dropbox = Path(self.args.remote_dropbox, self.path)

        cmd = f"scp {self.local_path} {self.args.remote_host}:{self.args.remote_dropbox}/Working/"
        self.log.debug(cmd)
        self.process_jpeg_cp = subprocess.Popen(shlex.split(cmd))

        self.manifest.write()

        cmd = f"scp {self.manifest.get_file()} {self.args.remote_host}:{self.args.remote_dropbox}/Working/"
        self.log.debug(cmd)
        self.process_json_cp = subprocess.Popen(shlex.split(cmd))


    def move_results(self):

        cmd = f"ssh bigbox 'mv {self.args.remote_dropbox}/Working/{self.manifest.get_file().name} {self.args.remote_dropbox}/Working/{self.path.name} {self.args.remote_dropbox}/Inbox/'"
        self.log.debug(cmd)
        self.process_move = subprocess.Popen(shlex.split(cmd))


    def is_copied(self):
        if self.copied:
            return True
        
        if self.process_json_cp.poll() == None:
            return False
        
        if self.process_jpeg_cp.poll() == None:
            return False

        # If we get here, it must have been copied!
        self.copied = True
        return True


    def is_moved(self):
        if self.moved:
            return True

        if self.process_move.poll() == None:
            return False

        self.moved = True
        return True


    def is_cleaned(self):
        return self.cleaned


    def cleanup(self):
        self.manifest.cleanup()
        os.remove(self.local_path)
        self.cleaned = True