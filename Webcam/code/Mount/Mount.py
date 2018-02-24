
import shlex
import subprocess

from ..CustomLogging import Log

class Mount:

    def __init__(self):
        self.log = Log()
        pass


    def is_mounted(self, folder):
        ps = subprocess.run(shlex.split("mountpoint /home/jmurray/ZFS"), 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
        self.log.debug(f"Got: {ps.returncode}")
        self.log.debug(f"{ps.stdout}")
        self.log.debug(f"{ps.stderr}")


        pass


    def _mount(self, folder):
        pass
        # sshfs -o allow_other,IdentityFile=~/.ssh/id_rsa jmurray@192.168.1.2:/ZFS/Media ~/ZFS
