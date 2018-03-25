from astral import Location
import asyncio
import datetime
import logging
import numpy as np
import sanic
import sanic
import time

from .Controllers import AstralController, PID, DummyController
from .CustomLogging import Log
from .Devices import Heater, Dimmer2, Dimmer3
from .Sensors import TMP102, TMP006, Si7021

class DragonHab:

    def __init__(self, args): 

        # Heater Lamp Config
        P = 22
        I = 0.008
        default_I = 30
        Integrator_min = -30

        # Basking Lamp and UV Config
        basking_lamp_setting = 57
        uv_trigger = basking_lamp_setting - 1

        # Ambient Temperatures
        ambient_day_temperature = 24.4444
        ambient_night_temperature = 21.1111



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

        tmp_controller = AstralController(args, 'astr0', "35°18'N", "105°06'W",  
            elivation=0, day_value=basking_lamp_setting, night_value=0, 
            report_times=True)
        self.devices['dimmer0'].bind(tmp_controller, 1)
        
        # Commented out until we get proper venting of the vivarium
        self.devices['dimmer0'].bind(tmp_controller, 4, override=uv_trigger)

        tmp_controller = AstralController(args, 'astrPID', "35°18'N", "105°06'W",  
            elivation=0, day_value=ambient_day_temperature, night_value=ambient_night_temperature)
        tmp_controller = PID(args, 'PID-ch2', self.sensors['t0'], 
            'temperature', P=P, I=I, Integrator=default_I/I, 
            Integrator_min=Integrator_min,
            astral_adjuster=tmp_controller)

        # tmp_controller.set_point= 26.6667
        self.devices['dimmer0'].bind(tmp_controller, 2)
        self.devices['dimmer0'].bind(tmp_controller, 3, gain=0.5)

        self.next_metric_log = datetime.datetime.now()
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
                    next_update += datetime.timedelta(seconds = self.args.update_delay)
                if loops > 0:
                    self.log.warning(f"Main loop catching up. Added {loops}x{self.args.update_delay}={loops * self.args.update_delay}s")

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


            if datetime.datetime.now() > self.next_metric_log:
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
                value = self.devices['dimmer0'].channels[1]['setting']
                self.log.metric(name="dimmer0.astral1.setting", generic_float=value)
                value = self.devices['dimmer0'].channels[4]['setting']
                self.log.metric(name="dimmer0.UV.setting", generic_float=value)

                # Record PID settings

                value = await self.devices['dimmer0'].channels[2]['controller'].astral_adjuster.get_value()
                self.log.metric(name="dimmer0.astralPID.setting", generic_float=value)

                self.next_metric_log += datetime.timedelta(seconds=self.args.log_delay)
                if datetime.datetime.now() > self.next_metric_log:
                    self.log.warning(f"Next metric log has already passed! {self.next_metric_log - datetime.datetime.now()} ago.")

        finally:
            self.update_in_progress = False


    async def hold_handler(self, request, channel, setting=None):

        if request.method == 'GET':
            self.log.info(f"Rquest to get channel data for channel {channel}")
            return sanic.response.json({'channel':channel,
                'setting':self.devices['dimmer0'].channels[channel]['hold']})

        elif request.method in ['POST','PUT']:
            self.log.info(f"Rquest to set channel {channel} to {setting}")
            # Limit setting to [-1,100]
            setting = int(setting)
            setting = max(-1,setting)
            setting = min(100,setting)
            self.devices['dimmer0'].channels[channel]['hold'] = setting
            return sanic.response.json({'channel':channel,'hold':setting})


    async def poke_handler(self, request):

        for channel in range(1,4+1):
            self.devices['dimmer0'].channels[channel]['poke'] = True
        return sanic.response.text("Poked all 4 channels")