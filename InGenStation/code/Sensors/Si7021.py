
import smbus2
import datetime
import asyncio
import time

from ..CustomLogging import Log

class Si7021:

    valid_addresses = [0b01000000,] # 0x40

    MEASURE_HUMIDITY_HOLD = 0xE5
    MEASURE_HUMIDITY_NO_HOLD = 0xF5
    MEASURE_TEMPERATURE_HOLD = 0xE3
    MEASURE_TEMPERATURE_NO_HOLD = 0xF3
    READ_TEMPERATURE_FROM_RH = 0xE0
    RESET = 0xFE

    WRITE_HEATER_CONTROL_REGISTER = 0x51
    READ_HEATER_CONTROL_REGISTER = 0x51
    HEATER_MASK = 0x0F # 0x00 for minimal heat, 0x0F for max. Must set heater 
    # to on before use!

    WRITE_USER_REGISTER = 0xE6
    READ_USER_REGISTER = 0xE7
    RES_1 = 0x01
    RES_2 = 0x10
    RES_3 = 0x11
    RES_4 = 0x00
    CHIP_HEATER_ENABLE = 0x04
    VDDS = 0x40

    def __init__(self, address, args):
        self.log = Log()
        self.args = args
        if address not in self.valid_addresses: 
            raise ValueError("Address not in value addresses")
        self.address = address
        self.last_update = datetime.datetime.min


    def configure(self):
        pass


    def __str__(self):
        return f"VEML(a=0x{self.address:_x}, t_obj={self.temperature:8.3f}, t_a={self.temperature_a:8.3f})"


    @property
    def data(self):
        return {"last_update":self.last_update, "temperature":self.temperature,
                "humidity":self.humidity, "raw_h":hex(self._humidity), 
                "raw_t":hex(self._temperature), "address":self.address,
                "update_age": str(datetime.datetime.now() - self.last_update)}


    @property
    def temperature(self):
        return (175.72 * self._temperature / 65536) - 46.85


    @property
    def humidity(self):
        return (125 * self._humidity / 65536) - 6


    async def update(self):
        t_start = time.time()
        self.log.debug(f"Updating Si7021 sensor 0x{self.address:02x}")
        with smbus2.SMBusWrapper(1) as bus:
            self._humidity = await self._measure_humidity(bus, 50)
            self._temperature = await self._measure_temperature(bus, 50)
        self.last_update = datetime.datetime.now()
        self.log.debug(f"Updated Si7021 sensor 0x{self.address:02x}, took {(time.time()-t_start)/1e3:.3f} ms")
        self.log.debug(f"Temperature was {self.temperature:.1f} C and humidity was {self.humidity:.1f}%")


    async def _measure_humidity(self, bus, max_loops):
        write = smbus2.i2c_msg.write(self.address, [self.MEASURE_HUMIDITY_HOLD])
        bus.i2c_rdwr(write)
        read = smbus2.i2c_msg.read(self.address, 2)
        loop = 0
        while loop < max_loops:
            try:
                bus.i2c_rdwr(read)
                break
            except OSError:
                loop += 1
                continue
        return (list(read)[0] << 8) + list(read)[1]

    async def _measure_temperature(self, bus, max_loops):
        write = smbus2.i2c_msg.write(self.address, [self.MEASURE_TEMPERATURE_HOLD])
        bus.i2c_rdwr(write)
        read = smbus2.i2c_msg.read(self.address, 2)
        loop = 0
        while loop < max_loops:
            try:
                bus.i2c_rdwr(read)
                break
            except OSError:
                loop += 1
                continue
        return (list(read)[0] << 8) + list(read)[1]