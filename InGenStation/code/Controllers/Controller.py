
from ..State import State

class Controller:

    def __init__(self):
        self.state = State.STARTUP
        pass


    async def update(self):
        raise NotImplimented("Base Controller class shouldn't be used.")


    async def get_value(self, setting=None):
        raise NotImplimented("Base Controller class shouldn't be used.")


    async def set_value(self, setting, value):
        raise NotImplimented("Base Controller class shouldn't be used.")

