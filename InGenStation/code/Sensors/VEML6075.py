
import smbus2
import datetime
import asyncio
import time

from ..CustomLogging import Log

class TMP106:

    valid_addresses = [0b00010100,]

    REGISTER_CONF      = 0x00
    REGISTER_UVA       = 0x07
    REGISTER_UVB       = 0x09
    REGISTER_COMP1     = 0x0A
    REGISTER_COMP2     = 0x0B
    REGISTER_DEVICE_ID = 0x0C

    UV_IT_50MS  = 0b00000000
    UV_IT_100MS = 0b00010000
    UV_IT_200MS = 0b00100000
    UV_IT_400MS = 0b00110000
    UV_IT_800MS = 0b01000000
    HD          = 0b00001000
    UV_TRIG     = 0b00000100
    UV_AF       = 0b00000010
    SD          = 0b00000001

    A = 2.22
    B = 1.33
    C = 2.95
    D = 1.74
    UVA_RESPONSE = 0.93
    UBB_RESPONSE = 2.1


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
        # self.log.debug(f"Updating TMP106 sensor 0x{self.address:02x}")
        # Fake write to sensor

        if self.args.purpose == 'test':
            import random
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

