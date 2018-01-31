
import smbus2
import datetime
import asyncio
import time
import numpy as np
import atexit

from ..CustomLogging import Log

class Dimmer2:

    valid_addresses = [0x27, 0x26, 0x25, 0x24, 0x23, 0x22, 0x21, 0x20,
                       0x3F, 0x3E, 0x3D, 0x3C, 0x3B, 0x3A, 0x39, 0x38]

    CH_1 = 0x80
    CH_2 = 0x81
    CH_3 = 0x82
    CH_4 = 0x83

    def __init__(self, name, address, args):
        self.log = Log()
        self.name = name
        self.args = args

        if address not in self.valid_addresses: 
            raise ValueError("Address not in value addresses")

        self.address = address
        self.last_update = datetime.datetime.min
        self.last_write = 0


    def configure(self):
        pass


    def __str__(self):
        return f"Dimmer(a=0x{self.address:_x}, Values: {self.values[1]}, {self.values[2]}, {self.values[3]}, {self.values[4]})"


    async def update(self):
        pass

    async def setOutput(self, channel, value):
        value = int(np.clip(100-value, 0, 100))
        channel = 0x7F+channel
        # We must not attempt to write more than once every 10 ms, or the device will not accept the commands!
        if time.time() - self.last_write < 0.01:
            time.sleep(0.01)
        with smbus2.SMBusWrapper(1) as bus:
            bus.write_word_data(self.address, channel, value)
        self.last_write = time.time()
