import asyncio
import logging
import sanic
import time
from .Sensors import TMP102, TMP106, Si7021
from .Devices import Heater
from .CustomLogging import Log

class RoachHab:

    def __init__(self, args): 
        self.log = Log()

        self.args = args
        self.sensors = {}
        self.sensors['t0'] = TMP102(0x48, args)
        # self.sensors['t1'] = TMP106(0x41, args)
        # self.sensors['t2'] = TMP106(0b1000101, args)
        self.sensors['h1'] = Si7021(0x40, args)

        self.devices = {}
        self.devices['heater0'] = Heater("heater0", args) 

        addresses = set()
        for sensor in self.sensors:
            if self.sensors[sensor].address in addresses:
                raise KeyError("Two sensors cannot share the same address")
            addresses.add(self.sensors[sensor].address)

        self.update_in_progress = False
        # TODO: Check to see if a settings file exists


    async def run(self):
        try:
            while True:
                t = time.time()

                await self.update()
                await self.log_sensors()

                t_sleep = self.args.update_freq - (time.time() - t)
                t_sleep = max(0, t_sleep)
                self.log.debug(f"Sleep for {t_sleep:.3f} s")
                await asyncio.sleep(t_sleep)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.log.exception("Caught an exception")
            self.log.info("Sleeping for 60 seconds before we continue")
            await asyncio.sleep(60)


    ### TEMPERATURE READINGS ###
    async def update(self):
        self.log.debug("Update sensors")
        t = time.time()
        if self.update_in_progress:
            self.log.warning("Cannot start an update when we are already doing one.")
            return
        try:
            self.update_in_progress = True   
            for sensor in self.sensors:
                await self.sensors[sensor].update()
            # self.devices['heater0'].update(self.sensors["t0"].temperature)
        finally:
            self.update_in_progress = False
            self.log.info(f"Sensor update completed, took {(time.time()-t)*1e3:.3f} ms")


    async def log_sensors(self):
        self.log.debug("Run metrics logging")
        self.log.metric(name="t0.temp", generic_float=self.sensors["t0"].temperature)
        self.log.metric(name="h1.temp", generic_float=self.sensors["h1"].temperature)
        self.log.metric(name="h1.humidity", generic_float=self.sensors["h1"].humidity)


    async def temperature_handler(self, request, sensor_id):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request for temperature received against id {sensor_id}")
        return sanic.response.json({sensor_id: self.sensors[sensor_id].data})


    async def all_temperature_handler(self, request):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request for temperature received against all sensors")
        data = {}
        for key in self.sensors:
            data[key] = self.sensors[key].data
        return sanic.response.json(data)

    async def heater_on(self, request):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request to turn heater on")
        self.devices['heater0'].on()
        return sanic.response.text("Heater on")

    async def heater_off(self, request):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request to turn heater off")
        self.devices['heater0'].off()
        return sanic.response.text("Heater off")

    async def heater_disabled(self, request):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request to disable heater")
        self.devices['heater0'].disable()
        return sanic.response.text("Heater disabled")