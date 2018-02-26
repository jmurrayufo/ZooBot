from astral import Location
import asyncio
import datetime
import logging
import numpy as np
import sanic
import time

from .Controllers import AstralController, PID, DummyController
from .CustomLogging import Log
from .Devices import Heater, Dimmer2, Dimmer3
from .Sensors import TMP102, TMP006, Si7021

class DragonHab:

    def __init__(self, args): 
        self.log = Log()

        self.args = args
        self.sensors = {}
        self.sensors['t0'] = TMP102(0x48, args)
        # self.sensors['t_ir1'] = TMP006(0x41, args)
        # self.sensors['t2'] = TMP106(0b1000101, args)
        # self.sensors['h1'] = Si7021(0x40, args)

        self.devices = {}
        # Check this in under the test group
        self.devices['dimmer0'] = Dimmer3("dimmer0", 0x3F, args) 

        tmp_controller = AstralController(args, 'astr0', "35°18'N", "105°06'W", 0)
        self.devices['dimmer0'].bind(tmp_controller, 1)
        # Commented out until we get proper venting of the vivarium
        # self.devices['dimmer0'].bind(tmp_controller, 4, override=True)

        tmp_controller = PID(args, 'PID-ch2', self.sensors['t0'], 
            'temperature', P=15.0, I=0.02, Integrator=30/0.02)
        tmp_controller.set_point= 23.8889
        self.devices['dimmer0'].bind(tmp_controller, 2)
        self.devices['dimmer0'].bind(tmp_controller, 3)

        self.last_metric_log = datetime.datetime.min
        addresses = set()
        for sensor in self.sensors:
            if self.sensors[sensor].address in addresses:
                raise KeyError("Two sensors cannot share the same address")
            addresses.add(self.sensors[sensor].address)

        self.update_in_progress = False
        self.setting = 0


    async def run(self):
        next_update = datetime.datetime.now()

        while True:
            try:

                await self.update()

                t_sleep = (next_update - datetime.datetime.now()).total_seconds()
                t_sleep = max(0, t_sleep)
                next_update += datetime.timedelta(seconds = self.args.update_delay)

                loops = 0
                while datetime.datetime.now() > next_update:
                    loops += 1
                    next_update += datetime.timedelta(seconds = args.update_delay)
                if loops > 0:
                    self.log.warning(f"Main loop catching up. Added {loops}x{args.update_delay}={loops * args.update_delay}s")

                await asyncio.sleep(t_sleep)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.log.exception("Caught an exception")
                self.log.info("Sleeping for 10 seconds before we continue")
                await asyncio.sleep(10)
                self.log.info("Sleep complete, continue")


    async def update(self):
        t = time.time()
        if self.update_in_progress:
            self.log.warning("Cannot start an update when we are already doing one.")
            return
        try:
            await self.devices['dimmer0'].update()

            for sensor in self.sensors:
                await self.sensors[sensor].update()


            if datetime.datetime.now() - self.last_metric_log > datetime.timedelta(seconds=self.args.log_delay):
                # self.log.debug("Log sensor data")
                # await self.log_sensors()
                self.log.metric(name="t0.temp", generic_float=self.sensors["t0"].temperature)
                pid = self.devices['dimmer0'].channels[2]['controller']
                values = await pid.get_value()
                # self.log.debug(f"Values were {values}")
                self.log.metric(name="dimmer0.pid2.total", generic_int=int(np.clip(sum(values),0,100)))
                self.log.metric(name="dimmer0.pid2.p1", generic_float=values[0])
                self.log.metric(name="dimmer0.pid2.i1", generic_float=values[1])
                self.log.metric(name="dimmer0.pid2.d1", generic_float=values[2])
                
                # Record current lamp settings
                value = await self.devices['dimmer0'].channels[1]['controller'].get_value()
                self.log.metric(name="dimmer0.astral1.setting", generic_int=value)


                self.last_metric_log = datetime.datetime.now()
                

        finally:
            self.update_in_progress = False
