import sanic
import asyncio
import logging
from Sensors import TMP102, TMP106

class RoachHab:

    def __init__(self, log): 
        self.log = log

        self.sensors = {}
        self.sensors['t0'] = TMP102(0b1001010, log)
        self.sensors['t1'] = TMP106(0b1000100, log)
        self.sensors['t2'] = TMP106(0b1000101, log)

        # TODO: Check to see if a settings file exists


    async def run(self):
        while True:
            self.log.debug("Update")
            for sensor in self.sensors:
                await self.sensors[sensor].update()
            await asyncio.sleep(60)


    ### TEMPERATURE READINGS ###


    def temperature_handler(self, request, sensor_id):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request for temperature received against id {sensor_id}")
        return sanic.response.json({sensor_id: self.sensors[sensor_id].data})


    def all_temperature_handler(self, request):
        # TODO: These really should just respond with data, and let a sanic
        # manager do the actual http stuff...
        self.log.info(f"Request for temperature received against all sensors")
        data = {}
        for key in self.sensors:
            data[key] = self.sensors[key].data
        return sanic.response.json(data)