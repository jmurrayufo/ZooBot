from .Controllers import AstralController, PID, DummyController
from .CustomLogging import Log
from .Devices import Heater, Dimmer2, Dimmer3
from .Sensors import TMP102, TMP006, Si7021
from .Sql import SQL
from astral import Location
import asyncio
import datetime
import datetime
import logging
import numpy as np
import sanic
import time

class DragonHab:

    def __init__(self, args): 
        self.log = Log()

        #self.sql = SQL(args)
        #self.sql.connect()

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
        self.devices['dimmer0'].bind(tmp_controller,1)

        tmp_controller = PID(args, 'PID-ch2', self.sensors['t0'], 
            'temperature', P=1.0, I=0.001)
        tmp_controller.set_point= 23.8889
        self.devices['dimmer0'].bind(tmp_controller,2)

        self.last_metric_log = datetime.datetime.min
        addresses = set()
        for sensor in self.sensors:
            if self.sensors[sensor].address in addresses:
                raise KeyError("Two sensors cannot share the same address")
            addresses.add(self.sensors[sensor].address)

        self.update_in_progress = False
        self.setting = 0


    async def run(self):
        while True:
            try:
                t = time.time()

                await self.update()

                t_sleep = self.args.update_delay - (time.time() - t)
                t_sleep = max(0, t_sleep)
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
                self.last_metric_log = datetime.datetime.now()
                if 't0' in self.sensors:
                    t = self.sensors['t0'].temperature
                    self.log.debug(f"Temperature is {t} C ({t * 9 / 5 + 32} F)")

                pid = self.devices['dimmer0'].channels[2]['controller']

                val = await pid.get_value()
                self.log.debug(f"PID Settings: P: {val[0]} I: {val[1]}")
                

        finally:
            self.update_in_progress = False
