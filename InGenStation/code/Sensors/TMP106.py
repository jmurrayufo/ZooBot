
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
        with smbus2.SMBusWrapper(1) as bus:
            self.basic_setup(bus, power_on=False, conv_rate=4)


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
            await self.power_crtl(bus, True)
            while 1:
                config = await self.get_config_reg(bus)
                if config & 0x0080:
                    break
                self.log.debug("Waiting on converstion...")
                await asyncio.sleep(1)


            self.log.debug(f"Config: {config:X}")
            data = []
            for i in [self.POINTER_OBJECT, self.POINTER_AMBIENMT]:
                write = smbus2.i2c_msg.write(self.address, [i])
                read = smbus2.i2c_msg.read(self.address, 2)
                bus.i2c_rdwr(write,read)
                read = list(read)
                data.append((read[0]<<8)+read[1])

            vObj = data[0]
            if vObj & 0x8000:
                vObj = (vObj - (1 << 16))
            vObj = vObj/2**15 * 5.12e-3 

            tDie = data[1]    
            if tDie & 0x8000:
                tDie = (tDie - (1 << 16))
                tDie >>= 2
            tDie = tDie * .03125
            tDie += 273.15

            # config = data[2]
            self.log.debug(f"Config: {config:X}")
            self.log.debug(f"  vObj: {vObj:8.3e} (0x{data[0]:04X})")
            self.log.debug(f"  tDie: {tDie-273.15:8.3f}/{tDie:8.3f} (0x{data[1]:04X})")
            S0 = 1.5e-14

            S = S0 * ( 1 + a1*(tDie - tRef) + a2*(tDie - tRef)**2 )
            self.log.debug(f"   d-r: {(tDie - tRef):8.3f}")
            self.log.debug(f"     S: {S:8.3f}")

            Vos = b0 + b1*(tDie - tRef) + b2*(tDie - tRef)**2
            self.log.debug(f"   Vos: {Vos:8.3f}")

            fVojb = (vObj - Vos) + c2*(vObj - Vos)**2
            self.log.debug(f" fVojb: {fVojb:8.3f}")

            Tobj = numpy.sqrt(numpy.sqrt( tDie**4 + (fVojb/S) ))
            adjust = 78
            self.log.debug(f"  Tobj: {Tobj-adjust:8.3f}")
            self.log.debug(f"  Tobj: {Tobj-273.15-adjust:8.3f}")
            self.log.debug(f" error: {37-(Tobj-273.15-adjust):8.3f}")

            cali = fVojb/( 1+ a1*(tDie - tRef) + a2*(tDie-tRef)**2 )
            self.log.debug(f"  cali: {cali}")
            self.log.debug(f"tDie^4: {tDie**4}")

            await self.power_crtl(bus, False)


        self.log.debug(f"Updated TMP106 sensor 0x{self.address:02x}, took {(time.time()-t_start)*1e3:.3f} ms")


    def basic_setup(self, bus, reset=False, power_on=True, conv_rate=4,
                          DRDY_pin=False, DRDY_bit=True):
        config = 0x0000
        if reset:
            config |= 0x8000 #0b10000000_00000000
        if power_on:
            config |= 0x7000 #0b01110000_00000000
        mask = {1:0x0<<9,
                2:0x1<<9,
                4:0x2<<9,
                8:0x3<<9,
               16:0x4<<9}
        config |= mask[conv_rate]
        if DRDY_pin:
            config |= 1<<8
        config_msb = (0xFF00 & config) >> 8
        config_lsb = (0x00FF & config)
        write = smbus2.i2c_msg.write(self.address, [0x02, config_msb, config_lsb])
        bus.i2c_rdwr(write)


    async def get_config_reg(self, bus):
        write = smbus2.i2c_msg.write(self.address, [0x02])
        read = smbus2.i2c_msg.read(self.address, 2)
        bus.i2c_rdwr(write,read)
        read = list(read)
        read = (read[0]<<8)+read[1]
        return read


    async def power_crtl(self, bus, power_on = True):
        # Disable or enable power
        config = await self.get_config_reg(bus)
        self.log.debug(f"Pre mod config: 0x{config:04X}")
        if power_on:
            config |= 0b0111000000000000
        else:
            config &= 0b1000111111111111
        self.log.debug(f"Post mod config: 0x{config:04X}")
        
        config_msb = (0xFF00 & config) >> 8
        config_lsb = (0x00FF & config)
        write = smbus2.i2c_msg.write(self.address, [0x02, config_msb, config_lsb]) 
        bus.i2c_rdwr(write)

        config_post = await self.get_config_reg(bus)
        self.log.debug(f"Wrote 0x{config:04X} and then read back 0x{config_post:04X}")