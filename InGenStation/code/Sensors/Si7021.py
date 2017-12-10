
import smbus2
import datetime
import asyncio
import time

from ..CustomLogging import Log

class Si7021:

    valid_addresses = [0b10000000,] # 0x80


    def __init__(self, address, args):
        self.log = Log()
        assert address in self.valid_addresses
        self.address = address
        self.last_update = datetime.datetime.min


    def __str__(self):
        return f"VEML(a=0x{self.address:_x}, t_obj={self.temperature:8.3f}, t_a={self.temperature_a:8.3f})"


    @property
    def data(self):
        return {"last_update":self.last_update, "temperature":self.temperature,
                "temperature_a":self.temperature_a, "address":self.address}


    @property
    def uva(self):
        """Last measured UVA value (raw)
        """
        return self._uva - self.A*self._uvcomp1 - self.B*_uvcomp2


    @property
    def uvb(self):
        """Last measured UVB value (raw)
        """
        return self._uvb - self.C*self._uvcomp1 - self.D*_uvcomp2


    async def update(self):
        t_start = time.time()
        import random
        self.log.debug(f"Updating TMP106 sensor 0x{self.address:02x}")
        # Fake write to sensor
        await asyncio.sleep(0.8)
        self._uva = random.randint(0,0xffff)
        self._uvb = random.randint(0,0xffff)
        self._uvcomp1 = random.randint(0,0xffff)
        self._uvcomp2 = random.randint(0,0xffff)
        self.last_update = datetime.datetime.now()
        self.log.debug(f"Updated TMP106 sensor 0x{self.address:02x}, took {(time.time()-t_start)/1e3:.3f} ms")
        
        return

        with smbus2.SMBusWrapper(1) as bus:

            bus.write_byte(self.address, 0, self.POINTER_OBJECT)
            self._temperature = bus.read_i2c_block_data(self.address, 0, 2)
            bus.write_byte(self.address, 0, self.POINTER_AMBIENMT)
            self._temperature_a = bus.read_i2c_block_data(self.address, 0, 2)

