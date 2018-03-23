
import smbus2
import datetime
import asyncio
import time
import pigpio

from ..CustomLogging import Log
from ..I2C import I2C, I2C2

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
        self.i2c = I2C2(baud=50000)
        self.last_update = datetime.datetime.min


    def configure(self):
        pass


    def reset(self, bus=None):
        time.sleep(0.015)
        self.i2c.Si7021_reset(self.address)
        time.sleep(0.015)



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
        return self._conv_temp(self._temperature)
    

    def _conv_temp(self, value):
        return (175.72 * value / 65536) - 46.85


    @property
    def humidity(self):
        return (125 * self._humidity / 65536) - 6


    async def update(self):
        t_start = time.time()
        # self.log.debug(f"Updating Si7021 sensor 0x{self.address:02x}")
        
        self._humidity = await self._measure_humidity(20)

        measured_temperature = await self._measure_temperature(20)

        # Handle boot loop!
        if not hasattr(self,"_temperature"): self._temperature = measured_temperature

        # Check the slope of the temperature for sudden changes
        delta_t_update = (datetime.datetime.now() - self.last_update).total_seconds()/60
        t_slope = (self._conv_temp(measured_temperature) - self._conv_temp(self._temperature))/delta_t_update

        # self.log.debug(f"Slospe measured to be {t_slope:.3f} C/min")
        if abs(t_slope) > 1:
            # Slope exceeded 1deg/minute!
            # self.log.warning(f"Saw excessive slope in temperature. Slope was {t_slope:.3f} C/min. Taking 5 measures and using the median.")
            # self.log.warning(f"This event was triggered from a temperature of {self._conv_temp(measured_temperature):.3f} C")
            t_list = []
            for i in range(5):
                self.reset()
                t_list.append(await self._measure_temperature(50))
            t_list = sorted(t_list)
            measured_temperature = t_list[2]

        self._temperature = measured_temperature

        self.last_update = datetime.datetime.now()
        # self.log.debug(f"Updated Si7021 sensor 0x{self.address:02x}, took {(time.time()-t_start)*1e3:.3f} ms")
        # self.log.debug(f"Temperature was {self.temperature:.1f} C (0x{self._temperature:04X}) and humidity was {self.humidity:.1f}% (0x{self._humidity:04X})")

    async def _measure_humidity(self, max_loops):

        loop = 0
        while loop < max_loops:
            loop += 1
            data = self.i2c.Si7021_humidity(self.address)
            crc = self._CRC_calc(data)
            if crc != data[2]:
                # self.log.warning(f"CRC Error. Values seen were {list(data)}, calculated crc was {crc}.")
                self.reset()
                time.sleep(0.02)
                continue
            break
        return (data[0] << 8) + data[1]


    async def _measure_temperature(self, max_loops):
        loop = 0
        time.sleep(0.02)
        while loop < max_loops:
            loop += 1
            data = self.i2c.Si7021_temperature(self.address)
            break
        return (data[0] << 8) + data[1]


    def _CRC_calc(self, data):
        # TODO: This can just use the crcmod tool with this example: x = crcmod.Crc(0b100110001,initCrc=0, rev=False, xorOut=0)

        crc = 0x00

        for i in range(len(data)-1):
            crc ^= data[i]
            for n in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x131
                else:
                    crc <<= 1

        return  crc
