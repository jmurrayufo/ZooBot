
import smbus2
import datetime
import asyncio
import time
import numpy as np
import atexit

from ..CustomLogging import Log

class Dimmer3:

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

        self.channels = {}
        self.channels[1] = {}
        self.channels[2] = {}
        self.channels[3] = {}
        self.channels[4] = {}

        self.address = address
        self.last_update = datetime.datetime.min
        self.last_write = 0


    def configure(self):
        pass


    def bind(self, controller, channel):
        """Given a valid Controller instance, bind it to controlling a given 
        channel.
        """
        self.log.info(f"Binding controller {controller} to channel {channel} on {self}")
        self.channels[channel]['controller'] = controller


    def overide(self, channel, setting, duration=None):
        """Given a valid channel and setting, override the current state to the 
        desired setting. If a duration is given, remove the override after 
        duration time. 
        """
        pass


    async def update(self):
        for i in range(1,4+1):
            if ['controller'] not in self.channels[i]:
                continue

            await self.channels[i]['controller'].update()
            val = await self.channels[i]['controller'].get_value()
            await self.setOutput(i,val)


    async def setOutput(self, channel, value):
        if value > 100 or value < 0:
            self.log.warning(f"{self} saw setOutput value of {value}, outside range [0,100]!")
        value = int(np.clip(100-value, 0, 100))
        channel = 0x7F+channel
        # We must not attempt to write more than once every 10 ms, or the device will not accept the commands!
        if time.time() - self.last_write < 0.01:
            time.sleep(0.01)
        with smbus2.SMBusWrapper(1) as bus:
            bus.write_word_data(self.address, channel, value)
        self.last_write = time.time()


    def __str__(self):
        return f"Dimmer3(addrs=0x{self.address:_x})"
