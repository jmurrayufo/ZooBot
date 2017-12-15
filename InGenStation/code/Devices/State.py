from enum import Enum, auto

class State(Enum):
    ON = auto()
    OFF = auto()
    ERROR = 0xFF
    UNKNOWN = 0xFE