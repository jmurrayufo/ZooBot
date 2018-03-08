
import os

class Ramdisk:
    """ Manage ram disk. """ 


    location = None


    def __init__(self, location=None):
        if location:
            Ramdisk.location = location


    def __str__(self):
        return f"Ramdisk({Ramdisk.location})"


    def fill_amount(self):
        # Returns number of free byes on disk
        stats = os.statvfs(Ramdisk.location)
        return stats.f_bfree * stats.f_bsize


    def fill_percent(self):
        # Returns currnt fill percentage
        stats = os.statvfs(Ramdisk.location)
        return 1 - (stats.f_bfree/stats.f_blocks)

