import enum
from lib.colors import ColorsEnum
import dataclasses


class SidesEnum(enum.Enum):
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4


def get_sides_for_color(int_color):
    if int_color == ColorsEnum.BLUE:
        return [SidesEnum.LEFT, SidesEnum.RIGHT]
    if int_color == ColorsEnum.RED:
        return [SidesEnum.TOP, SidesEnum.BOTTOM]


def get_color_for_side(side):
    if side in [SidesEnum.LEFT, SidesEnum.RIGHT]:
        return ColorsEnum.BLUE
    if side in [SidesEnum.TOP, SidesEnum.BOTTOM]:
        return ColorsEnum.RED
