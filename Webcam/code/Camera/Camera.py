

import shlex
import subprocess

from ..CustomLogging import Log


class Camera:
    """
    Known Controlls:
        Brightness
        Contrast
        Saturation
        White Balance Temperature, Auto
        Gain
        Power Line Frequency
        White Balance Temperature
        Sharpness
        Backlight Compensation
        Exposure, Auto
        Exposure (Absolute)
        Exposure, Auto Priority
        Pan (Absolute)
        Tilt (Absolute)
        Focus (absolute)
        Focus, Auto
        Zoom, Absolute
    """

    def __init__(self, args, dev_name):
        self.args = args
        self.dev = dev_name
        self.log = Log()


    def get_settings(self):

        settings = [
            "Brightness",
            "Contrast",
            "Saturation",
            "White Balance Temperature, Auto",
            "Gain",
            "Power Line Frequency",
            "White Balance Temperature",
            "Sharpness",
            "Backlight Compensation",
            "Exposure, Auto",
            "Exposure (Absolute)",
            "Exposure, Auto Priority",
            "Pan (Absolute)",
            "Tilt (Absolute)",
            "Focus (absolute)",
            "Focus, Auto",
            "Zoom, Absolute",
        ]

        for setting in settings:
            self.log.debug(f"Checking setting {setting}")
            cmd = f"uvcdynctrl -d /dev/video0 -g \"{setting}\""
            ps = subprocess.run(shlex.split(cmd), 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
            result = ps.stdout.decode("utf-8").rstrip()
            self.log.debug(f"Got: {result}")


