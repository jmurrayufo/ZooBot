
import hashlib

class MDFive:

    def __init__(self, file_path):
        self.file_path = file_path
        pass


    def checksum(self):
        hash_md5 = hashlib.md5()
        with open(self.file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()