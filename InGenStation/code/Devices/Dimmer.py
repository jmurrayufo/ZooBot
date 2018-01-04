
import smbus2
import datetime
import asyncio
import time

from ..CustomLogging import Log
from ..Sql import SQL

class Dimmer:

    valid_addresses = [0x27, 0x26, 0x25, 0x24, 0x23, 0x22, 0x21, 0x20,
                       0x3F, 0x3E, 0x3D, 0x3C, 0x3B, 0x3A, 0x39, 0x38]

    CH_1 = 0x80
    CH_2 = 0x81
    CH_3 = 0x82
    CH_4 = 0x83

    def __init__(self, name, address, args, devices):
        self.log = Log()
        self.name = name
        self.args = args
        if address not in self.valid_addresses: 
            raise ValueError("Address not in value addresses")
        self.address = address
        self.last_update = datetime.datetime.min
        self.sql = SQL()
        self.load_from_sql()

        if len(devices) != 4:
            raise IndexError("devices must be of len 4")

        self.devices = {}
        self.devices[1] = devices[0]
        self.devices[2] = devices[1]
        self.devices[3] = devices[2]
        self.devices[4] = devices[3]

        self.values = {}
        self.values[1] = 0
        self.values[2] = 0
        self.values[3] = 0
        self.values[4] = 0

        self.pid = {}
        self.pid[1] = PID(self.p1, self.i1, self.d1)
        self.pid[2] = PID(self.p2, self.i2, self.d2)
        self.pid[3] = PID(self.p3, self.i3, self.d3)
        self.pid[4] = PID(self.p4, self.i4, self.d4)
        self.pid[1].setPoint(self.set_point1)
        self.pid[2].setPoint(self.set_point2)
        self.pid[3].setPoint(self.set_point3)
        self.pid[4].setPoint(self.set_point4)

        self.log.info("Dimmer booted at address {}")



    def configure(self):
        pass


    def __str__(self):
        return f"Dimmer(a=0x{self.address:_x}, Values: {self.values[1]}, {self.values[2]}, {self.values[3]}, {self.values[4]})"


    async def update(self):
        self.load_from_sql()


    def load_from_sql(self):
        """Load current values from SQL
        """

        # self.log.debug("Loading values from SQL")
        self.p1 = self.sql.get_setting(self.name,'p1')
        self.i1 = self.sql.get_setting(self.name,'i1')
        self.d1 = self.sql.get_setting(self.name,'d1')
        self.set_point1 = self.sql.get_setting(self.name,'set_point1')

        self.p2 = self.sql.get_setting(self.name,'p2')
        self.i2 = self.sql.get_setting(self.name,'i2')
        self.d2 = self.sql.get_setting(self.name,'d2')
        self.set_point2 = self.sql.get_setting(self.name,'set_point2')

        self.p3 = self.sql.get_setting(self.name,'p3')
        self.i3 = self.sql.get_setting(self.name,'i3')
        self.d3 = self.sql.get_setting(self.name,'d3')
        self.set_point3 = self.sql.get_setting(self.name,'set_point3')

        self.p4 = self.sql.get_setting(self.name,'p4')
        self.i4 = self.sql.get_setting(self.name,'i4')
        self.d4 = self.sql.get_setting(self.name,'d4')
        self.set_point4 = self.sql.get_setting(self.name,'set_point4')



class PID:
    """
    Discrete PID control
    """

    def __init__(self, P=1.0, I=0.0, D=0.0, Derivator=0, Integrator=0, Integrator_max=100, Integrator_min=-100):

        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.Derivator=Derivator
        self.Integrator=Integrator
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min
        self.last_update = None

        self.set_point=0.0
        self.error=0.0

    def update(self, current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        self.error = self.set_point - current_value
        if self.last_update is None:
            self.last_update = datetime.datetime.now()
            self.D_value = 0
        else:
            dt = datetime.datetime.now() - self.last_update
            dt = dt.total_seconds()
            self.last_update = datetime.datetime.now()

            self.D_value = self.Kd * (self.error - self.Derivator)/dt
            self.Derivator = self.error
            self.Integrator = self.Integrator + self.error * dt

        self.P_value = self.Kp * self.error

        self.I_value = self.Integrator * self.Ki

        if self.I_value > self.Integrator_max:
            self.Integrator /= self.I_value/self.Integrator_max
        elif self.I_value < self.Integrator_min:
            self.Integrator /= self.I_value/self.Integrator_min

        self.I_value = self.Integrator * self.Ki

        self.I_value = self.Integrator * self.Ki

        PID = self.P_value + self.I_value + self.D_value
        self.log.debug(f"P: {self.P_value} I: {self.I_value}")
        self.log.debug(f"PID: {PID}")

        return PID

    def setPoint(self,set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0