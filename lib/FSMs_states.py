import enum


class StatesEnum(enum.IntEnum):
    CONNECT = 1
    WAIT_START = 2
    MAKE_MOVE = 3
    WAIT_MESSAGE = 4
    CLOSE = 5
    END = 0
