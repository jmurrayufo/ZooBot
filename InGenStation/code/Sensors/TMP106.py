
import smbus2
import datetime
import asyncio
import time
import numpy

from ..CustomLogging import Log

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
    POINTER_AMBIENMT = 0x01
    POINTER_CONFIG = 0x02
    POINER_MANU_ID = 0xFE
    POINTER_DEVICE_ID = 0xFF
    a1 = 1.75e-3
    a2 = -1.678e-5
    tRef = 298.15 #K
    b0 = -2.94e-5
    b1 = -5.7e-7
    b2 = 4.63e-9
    c2 = 13.4


    def __init__(self, address, args):
        self.log = Log()
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
        a1 = 1.75e-3
        a2 = -1.678e-5
        tRef = 298.15 #K
        b0 = -2.94e-5
        b1 = -5.7e-7
        b2 = 4.63e-9
        c2 = 13.4
        t_start = time.time()
        self.log.debug(f"Updating TMP106 sensor 0x{self.address:02x}")
        


        with smbus2.SMBusWrapper(1) as bus:
            data = []
            for i in [self.POINTER_OBJECT, self.POINTER_AMBIENMT, self.POINTER_CONFIG]:
                write = smbus2.i2c_msg.write(self.address, [i])
                read = smbus2.i2c_msg.read(self.address, 2)
                bus.i2c_rdwr(write,read)
                read = list(read)
                data.append((read[1]<<8)+read[0])
            vObj = data[0]
            tDie = data[1]
            config = data[2]
            self.log.debug(f"Config: {config:X}")
            self.log.debug(f"  vObj: {vObj:X}")
            self.log.debug(f"  tDie: {tDie:X}")
            S0 = 6e-14
            S = S0 * ( 1 + a1*(tDie - tRef) + a2*(tDie - tRef)**2 )
            Vos = b0 + b1*(tDie - tRef) + b2*(tDie - tRef)**2
            fVojb = (vObj - Vos) + c2*(vObj - Vos)**2
            Tobj = (tDie**4 + (fVojb/S))**(1/4)
            self.log.debug(f"TObject: {Tobj}")


        self.log.debug(f"Updated TMP106 sensor 0x{self.address:02x}, took {(time.time()-t_start)*1e3:.3f} ms")

