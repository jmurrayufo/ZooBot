

import datetime
import atexit

from .State import State
from ..CustomLogging import Log
import RPi.GPIO as GPIO

class Heater:
    """Controller for heater element
    """

    def __init__(self, name, args):
        self.log = Log()
        self.args = args
        self.name = name

        self.last_on = datetime.datetime.min
        self.last_off = datetime.datetime.now()

        self.max_on = datetime.timedelta(minutes=30)
        self.min_on = datetime.timedelta(seconds=60)

        self.max_off = datetime.timedelta(seconds=60) # This might not make sense?
        self.min_off = datetime.timedelta(seconds=120)

        self.temperature_limit_max = 40
        self.temperature_limit_min = 30

        self.state = State.OFF
        GPIO.setmode(GPIO.BCM)

        self.log.info("Heater Setup")
        GPIO.setup(20,GPIO.OUT)
        GPIO.setup(21,GPIO.OUT)
        self.log.info("Heater Setup Complete")

        self.log.info("Register exit function")
        atexit.register(_exit_function)


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
        self.log.info("Heater Enabled")
        GPIO.output(20,GPIO.LOW)
        GPIO.output(21,GPIO.HIGH)


    def disable(self, *, override=False):
        if self.state == State.OFF:
            return
        if self.state == State.ON and self.on_time < self.min_on:
            # TODO: Raise an error here?
            return
        self.state = State.OFF
        self.last_off = datetime.datetime.now()
        self.log.info("Heater Disabled")
        GPIO.output(20,GPIO.LOW)
        GPIO.output(21,GPIO.LOW)


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
                self.log.debug("Diable for max on time")
                self.disable()
            elif value > self.temperature_limit_max:
                self.log.debug("Diable for max temperature")
                self.disable()
        elif self.state == State.OFF:
            if self.off_time > self.max_off and 0:
                self.log.debug("Enable for max off time")
                self.enable()
            elif value < self.temperature_limit_min:
                self.log.debug("Enable for min temperature")
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

def _exit_function():
    log = Log()
    log.info("Cleanup before exit")
    GPIO.cleanup()

"""
#!/usr/bin/env python3.6

import time
#import rpi.gpio as GPIO
import RPi.GPIO as GPIO

try:
    print("Lets check this out!")

    print(f"Check mode: {GPIO.getmode()}")

    GPIO.setmode(GPIO.BCM)

    print("SETUP")
    GPIO.setup(20,GPIO.OUT)
    GPIO.setup(21,GPIO.OUT)

    print("ON")
    GPIO.output(20,GPIO.LOW)
    GPIO.output(21,GPIO.HIGH)

    time.sleep(10)

finally:
    print("OFF")
    GPIO.cleanup()
    pass
    """