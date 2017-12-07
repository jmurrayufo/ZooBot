
import smbus2
import datetime
import asyncio
import time
from ..CustomLogging import Log

class TMP102:

    valid_addresses = [0b1001000, 
                       0b1001001,
                       0b1001010,
                       0b1001011]

    P0 = 0b00000001
    P1 = 0b00000010


    def __init__(self, address):
        self.log = Log()
        assert address in self.valid_addresses
        self.address = address
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
            return (self._temperature - (1 << 12))*.0625
        else:
            return self._temperature*.0625


    async def update(self):
        t_start = time.time()
        import random
        self.log.debug(f"Updating TMP102 sensor 0x{self.address:02x}")
        self._temperature = random.randint(0,0xff)
        self.last_update = datetime.datetime.now()

        self.log.debug(f"Updated TMP102 sensor 0x{self.address:02x}, took {(time.time()-t_start)/1e3:.3f} ms")
        
        return

        with smbus2.SMBusWrapper(1) as bus:
            bus.write_byte(self.address, 0, 0)
            self._temperature = bus.read_byte(self.address)

