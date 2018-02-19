
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
    @param max_value Max output value of controller"""


    def __init__(self, args, name, lat, lon, elivation, max_value=100):

        super().__init__()
        self.log = Log()
        self.args = args
        self.name = name
        self.lat = lat
        self.lon = lon
        self.elivation = elivation
        self.max_value = max_value
        self.state = State.INITIALIZED
        self.update_in_progress = False
        self.today = None
        self.setting = None


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
                setting *= self.max_value 
                setting = int(setting)

            elif now > sunrise and now <= sunset:
                setting = self.max_value

            elif now > sunset and now <= dusk:
                setting = 1 - (now - sunset)/(dusk - sunset) 
                setting *= self.max_value 
                setting = int(setting)

            elif now > dusk:
                setting = 0

            # Debug override
            # setting = 100
            
            if self.setting != setting:
                self.setting = setting
                self.log.debug(f"Setting changed to {setting}")
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