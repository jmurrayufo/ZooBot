

from enum import Enum, auto

class State(Enum):
    DEGRADED = auto()
    ERROR = auto()
    HEALTHY = auto()
    INITIALIZED = auto()
    STARTUP = auto()
    TIMEDOUT = auto()
    UNKNOWN = auto()
