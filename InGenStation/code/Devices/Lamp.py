
import datetime

from .State import State

class Lamp:
    """Controller for lamp element
    """


    def __init__(self, args):
        self.args = args
        self.last_on = datetime.datetime.min
        self.state = State.OFF
        

    def __repr__(self):
        return f"{self.__class__.__name__}(state={self.state.name})"


    