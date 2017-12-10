
import smbus2
import datetime
import asyncio
import time

from ..CustomLogging import Log

class Si7021:

    valid_addresses = [0b10000000,] # 0x80

    MEASURE_HUMIDITY_HOLD = 0xE5
    MEASURE_HUMIDITY_NO_HOLD = 0xF5
    MEASURE_TEMPERATURE_HOLD = 0xE3
    MEASURE_TEMPERATURE_NO_HOLD = 0xF3
    READ_TEMPERATURE_FROM_RH = 0xE0
    RESET = 0xFE


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
                "humidity":self.humidity, "address":self.address}


    @property
    def temperature(self):
        return (175.72 * self._temperature / 65536) - 46.85


    @property
    def humidity(self):
        return (125 * self._humidity / 65536) - 6


    async def update(self):
        t_start = time.time()
        import random
        self.log.debug(f"Updating Si7021 sensor 0x{self.address:02x}")
        # Fake write to sensor
        await asyncio.sleep(0.8)
        self._temperature = random.randint(0,0xffff)
        self._humidity = random.randint(0,0xffff)
        self.last_update = datetime.datetime.now()
        self.log.debug(f"Updated Si7021 sensor 0x{self.address:02x}, took {(time.time()-t_start)/1e3:.3f} ms")
        
        return

        with smbus2.SMBusWrapper(1) as bus:

            bus.write_byte(self.address, 0, self.POINTER_OBJECT)
            self._temperature = bus.read_i2c_block_data(self.address, 0, 2)
            bus.write_byte(self.address, 0, self.POINTER_AMBIENMT)
            self._temperature_a = bus.read_i2c_block_data(self.address, 0, 2)

