from .CustomLogging import Log
from .Devices import Heater, Dimmer2
from .Sensors import TMP102, TMP106, Si7021
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
        # self.sensors['t0'] = TMP102(0x48, args)
        # self.sensors['t1'] = TMP106(0x41, args)
        # self.sensors['t2'] = TMP106(0b1000101, args)
        # self.sensors['h1'] = Si7021(0x40, args)

        self.devices = {}
        # self.devices['heater0'] = Heater("heater0", args, self.sensors['h1'])
        # Check this in under the test group
        self.devices['dimmer0'] = Dimmer2("dimmer0", 0x3F, args) 

        self.last_metric_log = datetime.datetime.min
        addresses = set()
        for sensor in self.sensors:
            if self.sensors[sensor].address in addresses:
                raise KeyError("Two sensors cannot share the same address")
            addresses.add(self.sensors[sensor].address)

        self.update_in_progress = False
        self.today = None
        self.setting = 0
        # TODO: Check to see if a settings file exists


    async def run(self):
        while True:
            try:
                t = time.time()

                await self.update()

                t_sleep = self.args.update_freq - (time.time() - t)
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
            self.update_in_progress = True   
            l = Location()
            l.name = 'Home'
            l.region = 'region'

            l.latitude = "35°18'N"
            l.longitude = "105°06'W"
            l.timezone = 'America/Denver'
            l.elevation = 0
            offset = datetime.timedelta(hours=1)

            sun = l.sun(date=datetime.date.today())

            dawn = (sun['dawn'] + offset).replace(tzinfo=None)
            sunrise = (sun['sunrise'] + offset).replace(tzinfo=None)
            sunset = (sun['sunset'] + offset).replace(tzinfo=None)
            dusk = (sun['dusk'] + offset).replace(tzinfo=None)

            if datetime.date.today() < datetime.date(2018,6,20):
                # Overide for baby dragon
                dawn = datetime.datetime.now().replace(hour=6, minute=16, second=00)
                sunrise = datetime.datetime.now().replace(hour=6, minute=45, second=54)
                sunset = datetime.datetime.now().replace(hour=21, minute=18, second=15)
                dusk = datetime.datetime.now().replace(hour=21, minute=48, second=9)

            if datetime.date.today() != self.today:
                if datetime.date.today() < datetime.date(2018,6,20):
                    self.log.info("New dragon overide protocall is in effect.")
                self.log.info("Todays times are as follows!")
                self.log.info(f"Dawn: {dawn}")
                self.log.info(f"Sunrise: {sunrise}")
                self.log.info(f"Sunset: {sunset}")
                self.log.info(f"Dusk: {dusk}")
                self.today = datetime.date.today()


            now = datetime.datetime.now()

            if now <= dawn: 
                setting = 0

            elif now > dawn and now <= sunrise:
                setting = (now - dawn)/(sunrise - dawn) 
                setting *= 100 
                setting = int(setting)

            elif now > sunrise and now <= sunset:
                setting = 100

            elif now > sunset and now <= dusk:
                setting = 1 - (now - sunset)/(dusk - sunset) 
                setting *= 100 
                setting = int(setting)

            elif now > dusk:
                setting = 0

            # Debug override
            setting = 100

            await self.devices['dimmer0'].setOutput(1,setting)
            await self.devices['dimmer0'].setOutput(2,setting)
            
            if self.setting != setting:
                self.setting = setting
                self.log.debug(f"Setting changed to {setting}")


        finally:
            self.update_in_progress = False
            # self.log.info(f"Sensor update completed, took {(time.time()-t)*1e3:.3f} ms")
