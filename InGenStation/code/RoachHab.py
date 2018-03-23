import asyncio
import logging
import sanic
import time
import datetime
from .Sensors import TMP102, TMP006, Si7021
from .Devices import Heater, Dimmer
from .CustomLogging import Log
from .Sql import SQL

class RoachHab:

    def __init__(self, args): 
        self.log = Log()

        self.sql = SQL(args)
        self.sql.connect()

        self.args = args
        self.sensors = {}
        self.sensors['t0'] = TMP102(0x48, args)
        # self.sensors['t1'] = TMP106(0x41, args)
        # self.sensors['t2'] = TMP106(0b1000101, args)
        self.sensors['h1'] = Si7021(0x40, args)

        self.devices = {}
        # self.devices['heater0'] = Heater("heater0", args, self.sensors['h1'])
        # Check this in under the test group
        self.devices['dimmer0'] = Dimmer("dimmer0", 0x3f, args, (self.sensors['h1'], None, None, None)) 

        self.next_metric_log = datetime.datetime.now()
        addresses = set()
        for sensor in self.sensors:
            if self.sensors[sensor].address in addresses:
                raise KeyError("Two sensors cannot share the same address")
            addresses.add(self.sensors[sensor].address)

        self.update_in_progress = False
        # TODO: Check to see if a settings file exists


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


    ### TEMPERATURE READINGS ###
    async def update(self):
        # self.log.debug("Update sensors")
        t = time.time()

        if self.update_in_progress:
            self.log.warning("Cannot start an update when we are already doing one.")
            return

        try:
            self.update_in_progress = True   
            for sensor in self.sensors:
                time.sleep(0.05)
                await self.sensors[sensor].update()
            for element in self.devices:
                time.sleep(0.05)
                await self.devices[element].update()
        
            if datetime.datetime.now() > self.next_metric_log:
                self.log_sensors()
                self.next_metric_log += datetime.timedelta(seconds=self.args.log_delay)
                if datetime.datetime.now() > self.next_metric_log:
                    self.log.warning(f"Next metric log has already passed! {self.next_metric_log - datetime.datetime.now()} ago.")

        finally:
            self.update_in_progress = False
            # self.log.info(f"Sensor update completed, took {(time.time()-t)*1e3:.3f} ms")


    async def log_sensors(self):
        # self.log.debug("Run metrics logging")
        self.log.metric(name="t0.temp", generic_float=self.sensors["t0"].temperature)
        self.log.metric(name="h1.temp", generic_float=self.sensors["h1"].temperature)
        self.log.metric(name="h1.humidity", generic_float=self.sensors["h1"].humidity)
        if "dimmer0" in self.devices:
            self.log.metric(name="dimmer0.value1", generic_int=self.devices["dimmer0"].values[1])
            self.log.metric(name="dimmer0.pid1.p1", generic_float=self.devices["dimmer0"].components[1]['p'])
            self.log.metric(name="dimmer0.pid1.i1", generic_float=self.devices["dimmer0"].components[1]['i'])
            self.log.metric(name="dimmer0.pid1.d1", generic_float=self.devices["dimmer0"].components[1]['d'])



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


    async def heater_state(self, request, state=None):
        # TODO: add a 'id' paramter to target different heaters
        if state == 'on':
            self.log.info(f"Request to turn heater on")
            self.devices['heater0'].on(override=True)
            return sanic.response.text("Heater on")

        elif state == 'off':
            self.log.info(f"Request to turn heater off")
            self.devices['heater0'].off(override=True)
            return sanic.response.text("Heater off")

        elif state == 'disable':
            self.log.info(f"Request to disable heater")
            self.devices['heater0'].disable(override=True)
            return sanic.response.text("Heater disabled")

        return sanic.response.text("Heater function")


    async def heater_settings(self, request):
        if request.method == 'GET':
            ret_json = {}
            ret_json['max_on'] = self.devices['heater0'].max_on.total_seconds()
            ret_json['max_off'] = self.devices['heater0'].max_off.total_seconds()
            ret_json['min_on'] = self.devices['heater0'].min_on.total_seconds()
            ret_json['min_off'] = self.devices['heater0'].min_off.total_seconds()
            ret_json['temperature_limit_max'] = self.devices['heater0'].temperature_limit_max
            ret_json['temperature_limit_min'] = self.devices['heater0'].temperature_limit_min
            self.log.debug(ret_json)
            return sanic.response.json(ret_json)
        elif request.method == 'POST':
            self.log.debug(f"Request given with form: {request.form}")
            for key in request.form:
                val = request.form[key][0]
                
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                self.sql.set_setting("heater0",key,val)
            self.devices['heater0'].load_from_sql()

            return sanic.response.text("POST")
        else:
            self.log.error(f"How did we even get here? Invalid method {request.method}")


    async def dimmer_settings(self, request):
        if request.method == 'GET':
            ret_json = {}
            ret_json['dimmer0'] = {}
            for idx in [1,2,3,4]:            
                ret_json['dimmer0'][f'pid{idx}'] = {}
                ret_json['dimmer0'][f'pid{idx}']['p'] = self.devices['dimmer0'].pid[idx].Kp
                ret_json['dimmer0'][f'pid{idx}']['i'] = self.devices['dimmer0'].pid[idx].Ki
                ret_json['dimmer0'][f'pid{idx}']['d'] = self.devices['dimmer0'].pid[idx].Kd
                ret_json['dimmer0'][f'pid{idx}']['set_point'] = self.devices['dimmer0'].pid[idx].set_point
                ret_json['dimmer0'][f'pid{idx}']['p_value'] = self.devices['dimmer0'].pid[idx].P_value
                ret_json['dimmer0'][f'pid{idx}']['i_value'] = self.devices['dimmer0'].pid[idx].I_value
                ret_json['dimmer0'][f'pid{idx}']['d_value'] = self.devices['dimmer0'].pid[idx].D_value
                ret_json['dimmer0'][f'pid{idx}']['output'] = self.devices['dimmer0'].pid[idx].output
                if self.devices['dimmer0'].devices[idx] is not None:
                    ret_json['dimmer0'][f'device{idx}'] = {}
                    ret_json['dimmer0'][f'device{idx}']['temperature'] = self.devices['dimmer0'].devices[idx].temperature
            self.log.debug(ret_json)
            return sanic.response.json(ret_json)
        elif request.method == 'POST':
            self.log.debug(request.form)

            for keyString in request.form:
                newValue = request.form[keyString][0]

                keys = keyString.split(".")
                device = keys[0]
                pidNum = int(keys[1][-1])
                key = keys[2]

                self.log.debug(f"Set device {device}, key {key}{pidNum} to {newValue}")

                self.sql.set_setting(device, f"{key}{pidNum}", newValue)

            return sanic.response.text("Updated")
        else:
            self.log.error(f"How did we even get here? Invalid method {request.method}")
            raise sanic.exceptions.ServerError