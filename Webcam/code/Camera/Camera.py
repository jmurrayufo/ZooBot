

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
        self.settings = {}


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
            cmd = f"uvcdynctrl -d /dev/video0 -g \"{setting}\""
            ps = subprocess.run(shlex.split(cmd), 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
            result = int(ps.stdout.decode("utf-8").rstrip())
            if setting not in self.settings:
                self.log.info(f"New setting discoerved, saving {setting} of {result}")
            elif self.settings[setting] != result:
                self.log.info(f"Setting {setting} has new value of {result}, changed from {self.settings[setting]}")
            self.settings[setting] = result

    def push_settings(self):

        for setting in self.settings:
            cmd = f"uvcdynctrl -d /dev/video0 -s \"{setting}\" {self.settings[setting]}"
            ps = subprocess.run(shlex.split(cmd), 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)

    def config_manual(self):
        self.settings["Brightness"] = 128
        self.settings["Contrast"] = 128
        self.settings["Saturation"] = 128
        self.settings["White Balance Temperature, Auto"] = 0
        self.settings["Gain"] = 179
        self.settings["Power Line Frequency"] = 2
        self.settings["White Balance Temperature"] = 4000
        self.settings["Sharpness"] = 128
        self.settings["Backlight Compensation"] = 0
        self.settings["Exposure, Auto"] = 3
        self.settings["Exposure (Absolute)"] = 333
        self.settings["Exposure, Auto Priority"] = 0
        self.settings["Pan (Absolute)"] = 0
        self.settings["Tilt (Absolute)"] = 0
        # self.settings["Focus (absolute)"] = 130
        self.settings["Focus, Auto"] = 1
        self.settings["Zoom, Absolute"] = 100

    def log_settings(self):

        for setting in self.settings:
            self.log.info(f"Setting {setting} has current value of {self.settings[setting]}")