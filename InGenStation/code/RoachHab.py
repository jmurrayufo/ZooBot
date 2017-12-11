import sanic
import asyncio
import logging
from .Sensors import TMP102, TMP106, Si7021
from .CustomLogging import Log

class RoachHab:

    def __init__(self, args): 
        self.log = Log()

        self.sensors = {}
        # self.sensors['t0'] = TMP102(0b1001010, args)
        # self.sensors['t1'] = TMP106(0b1000100, args)
        # self.sensors['t2'] = TMP106(0b1000101, args)
        self.sensors['h1'] = Si7021(0x40, args)

        # TODO: Check to see if a settings file exists


    async def run(self):
        while True:
            self.log.debug("Update")
            t = time.time()
            for sensor in self.sensors:
                await self.sensors[sensor].update()
            t_sleep = 60 - time.time() - t
            t_sleep = max(0, t_sleep)
            self.log.debug(f"Sleep for {t_sleep:.3f} s")
            await asyncio.sleep(t_sleep)


    ### TEMPERATURE READINGS ###


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