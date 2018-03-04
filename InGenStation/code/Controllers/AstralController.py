
from astral import Location
import datetime
import time

from ..CustomLogging import Log
from ..State import State
from .Controller import Controller

class AstralController(Controller):
    """Timer controller for various devices.
    @param args Arguments from the command line
    @param name Name of this controller
    @param astral Boolean value if this should calculate times on astral lib
    @param lat If astral is used, valid lat of location
    @param lon If astral is used, valid lon of location
    @param elevation If astral is used, valid elevation of location
    @param day_value Value during daytime operations
    @param night_value Value during nightime operations"""


    def __init__(self, args, name, lat, lon, elivation, day_value, night_value, report_times=False):

        super().__init__()
        self.log = Log()
        self.args = args
        self.name = name
        self.lat = lat
        self.lon = lon
        self.elivation = elivation
        self.state = State.INITIALIZED
        self.update_in_progress = False
        self.today = None
        self.setting_floor = night_value
        self.setting_offset = day_value - night_value
        self.setting = -1
        self.reported_setting = -1
        self.report_times = report_times

        self.last_delta_alarm = datetime.datetime.now()

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

            l.latitude = self.lat
            l.longitude = self.lon
            l.timezone = 'America/Denver'
            l.elevation = 0
            offset = datetime.timedelta(hours=1) # Offset to handle work better

            sun = l.sun(date=datetime.date.today())

            dawn = (sun['dawn'] + offset).replace(tzinfo=None)
            sunrise = (sun['sunrise'] + offset).replace(tzinfo=None)
            sunset = (sun['sunset'] + offset).replace(tzinfo=None)
            dusk = (sun['dusk'] + offset).replace(tzinfo=None)

            if False and datetime.date.today() < datetime.date(2018,6,20):
                # Overide for baby dragon
                if self.report_times and datetime.date.today() != self.today:
                    self.log.info("New dragon overide protocall is in effect.")

                dawn = datetime.datetime.now().replace(hour=6, minute=16, second=0)
                sunrise = datetime.datetime.now().replace(hour=6, minute=45, second=54)
                sunset = datetime.datetime.now().replace(hour=21, minute=18, second=15)
                dusk = datetime.datetime.now().replace(hour=21, minute=48, second=9)
                
                dawn = datetime.datetime.now().replace(hour=0, minute=0, second=0)
                sunrise = datetime.datetime.now().replace(hour=0, minute=25, second=0)
                sunset = datetime.datetime.now().replace(hour=0, minute=35, second=0)
                dusk = datetime.datetime.now().replace(hour=0, minute=59, second=59)

                dawn = dawn.replace(microsecond=0)
                sunrise = sunrise.replace(microsecond=0)
                sunset = sunset.replace(microsecond=0)
                dusk = dusk.replace(microsecond=0)

            if self.report_times and datetime.date.today() != self.today:
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
                setting *= self.setting_offset

            elif now > sunrise and now <= sunset:
                setting = self.setting_offset

            elif now > sunset and now <= dusk:
                setting = 1 - (now - sunset)/(dusk - sunset) 
                setting *= self.setting_offset 

            elif now > dusk:
                setting = 0

            setting += self.setting_floor

            if (self.reported_setting != setting and 
                    now - self.last_delta_alarm > datetime.timedelta(seconds=60)):
                self.log.debug(f"Setting on AstralController {self.name} changed from {self.reported_setting:.1f} to {setting:.1f}")
                self.last_delta_alarm = now
                self.reported_setting = setting

            self.setting = setting

        except:
            self.state = State.DEGRADED
            self.log.error(f"AstralController {self} is in a {self.state} state.")
            raise
        else:
            self.state = State.HEALTHY
        finally:
            self.update_in_progress = False
            # self.log.info(f"Sensor update completed, took {(time.time()-t)*1e3:.3f} ms")


    async def get_value(self, setting=None):
        return self.setting


    async def set_value(self, setting, value):
        try:
            getattr(self, setting)
        except AttributeError:
            self.log.warning(f"A value is being set for this object that didn't exist before now! Setting '{setting}' being set to value '{value}'")
        setattr(self, setting, value)


"""
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

            await self.devices['dimmer0'].setOutput(1,setting)
            await self.devices['dimmer0'].setOutput(2,setting)
            
            if self.setting != setting:
                self.setting = setting
                self.log.debug(f"Setting changed to {setting}")


        finally:
            self.update_in_progress = False
            # self.log.info(f"Sensor update completed, took {(time.time()-t)*1e3:.3f} ms")"""