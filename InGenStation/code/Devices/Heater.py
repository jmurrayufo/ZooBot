

import datetime

from .State import State
from ..CustomLogging import Log

class Heater:
    """Controller for heater element
    """

    def __init__(self, name, args):
        self.args = args
        self.name = name

        self.last_on = datetime.datetime.min
        self.last_off = datetime.datetime.now()

        self.max_on = datetime.timedelta(seconds=60)
        self.min_on = datetime.timedelta(seconds=10)

        self.max_off = datetime.timedelta(seconds=60) # This might not make sense?
        self.min_off = datetime.timedelta(seconds=10)

        self.temperature_limit_max = 40
        self.temperature_limit_min = 30

        self.state = State.OFF


    def __repr__(self):
        ret_val = f"{self.__class__.__name__}("
        ret_val += f"state={self.state.name}"
        if self.state == State.ON:
            ret_val += f", ontime={datetime.datetime.now() - self.last_on}"
        if self.state == State.OFF:
            ret_val += f", offtime={datetime.datetime.now() - self.last_off}"
        ret_val += f")"
        return ret_val


    def enable(self, *, override=False):
        if self.state == State.ON:
            return
        if self.state == State.OFF and self.off_time < self.min_off:
            # TODO: Raise an error here?
            return
        self.state = State.ON
        self.last_on = datetime.datetime.now()


    def disable(self, *, override=False):
        if self.state == State.OFF:
            return
        if self.state == State.ON and self.on_time < self.min_on:
            # TODO: Raise an error here?
            return
        self.state = State.OFF
        self.last_off = datetime.datetime.now()


    def toggle(self):
        if self.state == State.OFF:
            self.enable()
            return
        elif self.state == State.ON:
            self.disable()
            return


    def update(self, value):
        """Update the device with it's current feedback values

        This may result in a state change 
        """
        if self.state == State.ON:
            if self.on_time > self.max_on:
                self.disable()
            elif value > self.temperature_limit_max:
                self.disable()
        elif self.state == State.OFF:
            if self.off_time > self.max_off:
                self.enable()
            elif value < self.temperature_limit_min:
                self.enable()


    @property
    def on_time(self):
        if self.state == State.ON:
            return datetime.datetime.now() - self.last_on
        return datetime.timedelta(0)


    @property
    def off_time(self):
        if self.state == State.OFF:
            return datetime.datetime.now() - self.last_off
        return datetime.timedelta(0)


    def is_on(self):
        return self.state == State.ON


    def is_off(self):
        return self.state == State.OFF
