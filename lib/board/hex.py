import dataclasses
from lib.board.sides import SidesEnum
from lib.colors import ColorsEnum
from typing import Optional
from lib.board.moves import Move


@dataclasses.dataclass(frozen=True)
class Hex:
    move: Move
    color: ColorsEnum
    side: Optional[SidesEnum] = dataclasses.field(default=None)
    distance_from_start: float = dataclasses.field(default=float('inf'))

    # def __init__(self, move, color, side=None):
    #     self.side = side
    #     self.distance_from_start = float("inf")
    #     self.color = color
    #     self.move = move
