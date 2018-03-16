
import smbus2
import datetime
import asyncio
import time

from ..CustomLogging import Log
from ..I2C import I2C, I2C2

class TMP102:

    valid_addresses = [0b1001000, 
                       0b1001001,
                       0b1001010,
                       0b1001011]

    P0 = 0b00000001
    P1 = 0b00000010


    def __init__(self, address, args):
        self.log = Log()
        self.args = args
        assert address in self.valid_addresses
        self.address = address
        self.i2c = I2C2()
        self.last_update = datetime.datetime.min


    def __str__(self):
        return f"TMP102(a=0x{self.address:_x}, t={self.temperature:6.1f})"


    @property
    def data(self):
        return {"last_update":str(self.last_update), 
                "temperature":self.temperature, "address":self.address,
                "update_age": str(datetime.datetime.now() - self.last_update)}


    @property 
    def temperature(self):
        if self._temperature & 0x800:
            # This is a negative number, flip it!
            temp = (self._temperature - (1 << 12))
        else:
            temp = self._temperature
        temp *= 0.0625
        return temp


    async def update(self):

        self._temperature = self.i2c.TMP102_temperature(self.address)
        self._temperature = (self._temperature[0] << 8) + self._temperature[1]
        self._temperature >>= 4


        self.last_update = datetime.datetime.now()
        # self.log.debug(f"Updated TMP102 sensor 0x{self.address:02x}, took {(time.time()-t_start)*1e3:.3f} ms")
        # self.log.debug(f"Temperature was {self.temperature:.1f} C")
