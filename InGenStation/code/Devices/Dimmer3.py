
import smbus2
import datetime
import asyncio
import time
import numpy as np
import atexit

from ..CustomLogging import Log

class Dimmer3:

    valid_addresses = [0x27, 0x26, 0x25, 0x24, 0x23, 0x22, 0x21, 0x20,
                       0x3F, 0x3E, 0x3D, 0x3C, 0x3B, 0x3A, 0x39, 0x38]

    CH_1 = 0x80
    CH_2 = 0x81
    CH_3 = 0x82
    CH_4 = 0x83

    def __init__(self, name, address, args):
        self.log = Log()
        self.name = name
        self.args = args

        if address not in self.valid_addresses: 
            raise ValueError("Address not in value addresses")

        self.channels = {}
        self.channels[1] = {'setting':-1, 
                            'hold':-1, 
                            'poke':False,
                            'last_bounds_error':datetime.datetime.min}
        self.channels[2] = {'setting':-1, 
                            'hold':-1, 
                            'poke':False,
                            'last_bounds_error':datetime.datetime.min}
        self.channels[3] = {'setting':-1, 
                            'hold':-1, 
                            'poke':False,
                            'last_bounds_error':datetime.datetime.min}
        self.channels[4] = {'setting':-1, 
                            'hold':-1, 
                            'poke':False,
                            'last_bounds_error':datetime.datetime.min}

        self.address = address
        self.last_update = datetime.datetime.min
        self.last_write = 0

        if not args.purpose == 'test':
            atexit.register(_exit_function, address=self.address)


    def configure(self):
        pass


    def bind(self, controller, channel, override=False):
        """Given a valid Controller instance, bind it to controlling a given 
        channel.
        """
        self.log.info(f"Binding controller {controller} to channel {channel} on {self}")
        self.channels[channel]['controller'] = controller
        self.channels[channel]['override'] = override


    def overide(self, channel, setting, duration=None):
        """Given a valid channel and setting, override the current state to the 
        desired setting. If a duration is given, remove the override after 
        duration time. 
        """
        pass


    async def update(self):
        for i in range(1,4+1):

            # Sleep for 10 ms between runs to allow I2C buss to reset?
            time.sleep(0.01)

            if 'controller' not in self.channels[i]:
                continue

            await self.channels[i]['controller'].update()
            val = await self.channels[i]['controller'].get_value()
            if type(val) == tuple:
                val = sum(val)

            if self.channels[i]['override']:
                if val > self.channels[i]['override']:
                    val = 100
                else:
                    val = 0

            # If we have a hold, honor it
            if self.channels[i]['hold'] != -1:
                val = self.channels[i]['hold']

            if self.channels[i]['override'] and val != self.channels[i]['setting']:
                self.log.debug(f"Channel {i} set from {self.channels[i]['setting']} to {val}")

            # Prevent noisy lights at night!
            if val != self.channels[i]['setting'] or self.channels[i]['poke']:
                self.channels[i]['setting'] = val
                await self.setOutput(i,val)
                self.channels[i]['poke'] = False


    async def setOutput(self, channel, value):
        now = datetime.datetime.now()
        lbe = self.channels[channel]['last_bounds_error']
        if ((value > 100 or value < 0)
                and channel != 3
                and lbe - now > datetime.datetime.timedelta(seconds=15)):
            self.channels[channel]['last_bounds_error'] = datetime.datetime.now()
            self.log.warning(f"{self} saw setOutput value of {value:.3f}, outside range [0,100]!")

        value = int(np.clip(100-value, 0, 100))

        channel = 0x7F+channel

        if channel not in [self.CH_1, self.CH_2, self.CH_3, self.CH_4]:
            self.log.critical(f"Attempted to write to channel 0x{channel:0X}, which is invalid!")
            raise IndexError(f"Channel 0x{channel:0X} is not a valid channel.")
        # We must not attempt to write more than once every 10 ms, or the device will not accept the commands!
        if time.time() - self.last_write < 0.1:
            time.sleep(0.1)
        with smbus2.SMBusWrapper(1) as bus:
            bus.write_word_data(self.address, channel, value)
        self.last_write = time.time()


    def __str__(self):
        return f"Dimmer3(addrs=0x{self.address:_x})"


def _exit_function(address):
    Log().info("Exiting, set power to 100 (full closed)")
    with smbus2.SMBusWrapper(1) as bus:
        for ch in [0x80, 0x81, 0x82, 0x83]:
            msg = smbus2.i2c_msg.write(address, [ch, 100])
            bus.i2c_rdwr(msg)