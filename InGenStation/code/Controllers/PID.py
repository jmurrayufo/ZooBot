
import datetime
import time

from ..CustomLogging import Log
from .Controller import Controller

class PID(Controller):
    """
    Discrete PID control
    """

    def __init__(self, args, name, sensor, sensor_attrib
        P=1.0, I=0.0, D=0.0, 
        Derivator=0, 
        Integrator=0, Integrator_max=100, Integrator_min=-100):

        self.log = Log()
        self.P_value = 0
        self.I_value = 0
        self.D_value = 0
        self.output = 0
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.sensor = sensor
        self.sensor_attrib
        self.Derivator = Derivator
        self.Integrator = Integrator
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min
        self.last_update = None

        self.set_point = 0.0
        self.error = 0.0

    async def update(self):
        """
        Calculate PID output value for given reference input and feedback
        """

        # Get current value
        await self.sensor.update()
        current_value = getattr(self.sensor, self.sensor_attrib)

        self.error = self.set_point - current_value
        # print(f"Error: {self.set_point:.3f} - {current_value:.3f} = {self.error:.3f}")
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

        # PID = self.P_value + self.I_value + self.D_value
        # print(f"P: {self.P_value} I: {self.I_value}")
        # print(f"PID: {self.P_value + self.I_value + self.D_value}")
        self.output = self.P_value + self.I_value + self.D_value
        return (self.P_value, self.I_value, self.D_value)

    async def get_value(self, setting=None):
        return (self.P_value, self.I_value, self.D_value)

    async def set_value(self, setting, value):
        """
        Initilize the setpoint of PID
        """
        try:
            getattr(self, setting)
        except AttributeError:
            self.log.warning(f"A value is being set for this object that didn't exist before now! Setting '{setting}' being set to value '{value}'")
        setattr(self, setting, value)