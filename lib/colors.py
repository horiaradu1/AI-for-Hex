import enum
import dataclasses


class ColorsEnum(enum.IntEnum):
    RED = 1
    BLUE = 2
    FREE = 0


def char_to_int_color(char_color):
    if char_color == "R":
        return ColorsEnum.RED
    if char_color == "B":
        return ColorsEnum.BLUE
    return ColorsEnum.FREE


def int_color_to_char(int_color):
    if int_color == ColorsEnum.RED:
        return "R"
    if int_color == ColorsEnum.BLUE:
        return "B"
    return "0"


def get_oposing_color(int_color):
    if int_color == ColorsEnum.RED:
        return ColorsEnum.BLUE
    if int_color == ColorsEnum.BLUE:
        return ColorsEnum.RED
