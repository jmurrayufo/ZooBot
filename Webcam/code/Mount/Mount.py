
import shlex
import subprocess

from ..CustomLogging import Log

class Mount:

    def __init__(self):
        self.log = Log()
        pass


    def is_mounted(self, folder):
        ps = subprocess.run(shlex.split(f"mountpoint {folder}"), 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
        return ps.returncode == 0


    def mount(self, network_loc, folder):

        # cmd = f"sshfs -o allow_other,IdentityFile=/home/jmurray/.ssh/id_rsa jmurray@192.168.1.2:/ZFS/Media /home/jmurray/ZFS"
        cmd = f"sshfs -o allow_other,IdentityFile=/home/jmurray/.ssh/id_rsa {network_loc} {folder}"
        ps = subprocess.run(shlex.split(cmd), 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
