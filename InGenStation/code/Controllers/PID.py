
import datetime
import time

from ..CustomLogging import Log
from .Controller import Controller

class PID(Controller):
    """
    Discrete PID control
    """

    def __init__(self, args, name, sensor, sensor_attrib,
        P=1.0, I=0.0, D=0.0, 
        Derivator=0, 
        Integrator=0, Integrator_max=100, Integrator_min=-100,
        astral_adjuster=None, buffer_derivative=False):

        self.log = Log()
        self.P_value = 0
        self.I_value = 0
        self.D_value = 0
        self.output = 0
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.sensor = sensor
        self.sensor_attrib = sensor_attrib
        self.Derivator = Derivator
        self.Integrator = Integrator
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min
        self.last_update = None
        self.astral_adjuster = astral_adjuster
        self.buffer_derivative = buffer_derivative
        if buffer_derivative:
            self.d_buffer = []

        self.set_point = 0.0
        self.error = 0.0

    async def update(self):
        """
        Calculate PID output value for given reference input and feedback
        """

        # Get current value
        await self.sensor.update()
        current_value = getattr(self.sensor, self.sensor_attrib)

        # Adjust from the astral settings if needed
        if self.astral_adjuster is not None:
            await self.astral_adjuster.update()
            self.set_point = await self.astral_adjuster.get_value()

        self.error = self.set_point - current_value
        # print(f"Error: {self.set_point:.3f} - {current_value:.3f} = {self.error:.3f}")

        if self.last_update is None:
            self.last_update = datetime.datetime.now()
            self.D_value = 0
        else:
            dt = datetime.datetime.now() - self.last_update
            dt = dt.total_seconds()

            if dt < 1.0:
                return

            self.last_update = datetime.datetime.now()

            if not self.buffer_derivative:
                self.D_value = self.Kd * (self.error - self.Derivator)/dt
                self.Derivator = self.error
            else:
                #Append current error to the array
                self.d_buffer.append((datetime.datetime.now(),current_value))

                # Only save the last 15 minutes
                self.d_buffer = [x for x in self.d_buffer if datetime.datetime.now()-x[0] < datetime.timedelta(minutes=15)]

                d_error = current_value - self.d_buffer[0][1]

                self.D_value = self.Kd * d_error / (datetime.datetime.now()-self.d_buffer[0][0]).total_seconds()
                print(self.D_value,len(self.d_buffer))
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
        # self.log.debug(f"C: {current_value} S: {self.set_point} P: {self.P_value} I: {self.I_value} D:{self.D_value}")
        return

    async def get_value(self, setting=None):
        # self.log.debug("Pulling values")
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
