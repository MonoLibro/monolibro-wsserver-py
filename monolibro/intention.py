from enum import Enum


class Intention(Enum):
    DEBUG_INTENTION = -1
    BROADCAST = 0
    SPECIFIC = 1
    SYSTEM = 2