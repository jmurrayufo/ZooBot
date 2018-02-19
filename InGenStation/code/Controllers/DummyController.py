
import datetime
import time

from ..CustomLogging import Log
from ..State import State
from .Controller import Controller

class DummyController(Controller):
    """Timer controller for various devices.
    @param args Arguments from the command line
    @param name Name of this controller
    @param astral Boolean value if this should calculate times on astral lib
    @param lat If astral is used, valid lat of location
    @param lon If astral is used, valid lon of location
    @param elevation If astral is used, valid elevation of location
    @param max_value Max output value of controller"""


    def __init__(self, args, name):
        super().__init__()


    async def update(self):
        pass


    async def get_value(self, setting=None):
        return 100


    async def set_value(self, setting, value):
        pass
