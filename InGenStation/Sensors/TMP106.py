
import smbus2
import datetime
import asyncio
import time

class TMP106:

    valid_addresses = [0b1000000, 
                       0b1000001,
                       0b1000010,
                       0b1000011,
                       0b1000100,
                       0b1000101,
                       0b1000110,
                       0b1000111]

    POINTER_OBJECT = 0x00
    POINTER_AMBIENMT = 0x00
    POINTER_CONFIG = 0x02
    POINER_MANU_ID = 0xFE
    POINTER_DEVICE_ID = 0xFF


    def __init__(self, address, log):
        self.log = log
        assert address in self.valid_addresses
        self.address = address
        self.last_update = datetime.datetime.min


    def __str__(self):
        return f"TMP106(a=0x{self.address:_x}, t_obj={self.temperature:8.3f}, t_a={self.temperature_a:8.3f})"


    @property
    def data(self):
        return {"last_update":self.last_update, "temperature":self.temperature,
                "temperature_a":self.temperature_a, "address":self.address}


    @property 
    def temperature(self):
        ret_val = self._temperature
        if ret_val & 0x8000:
            ret_val = -((ret_val ^ 0xFFFF) + 1)
        # else:
        ret_val >>= 2
        return ret_val/32

    @property 
    def temperature_a(self):
        ret_val = self._temperature_a
        if ret_val & 0x8000:
            ret_val = -((ret_val ^ 0xFFFF) + 1)
        # else:
        ret_val >>= 2
        return ret_val/32


    async def update(self):
        t_start = time.time()
        import random
        self.log.info(f"Updating sensor 0x{self.address:02x}")
        self._temperature = random.randint(0,0xffff)
        self._temperature_a = random.randint(0,0xffff)
        self.last_update = datetime.datetime.now()
        self.log.info(f"Updated sensor 0x{self.address:02x}, took {(time.time()-t_start)/1e3:.3f} ms")
        
        return

        with smbus2.SMBusWrapper(1) as bus:
            bus.write_byte(self.address, 0, self.POINTER_OBJECT)
            self._temperature = bus.read_i2c_block_data(self.address, 0, 2)
            bus.write_byte(self.address, 0, self.POINTER_AMBIENMT)
            self._temperature_a = bus.read_i2c_block_data(self.address, 0, 2)

