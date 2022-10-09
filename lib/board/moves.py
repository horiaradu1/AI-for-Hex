from lib.colors import ColorsEnum
import dataclasses
import random
ACTIVE_REGION_BOUNDS = 2


@dataclasses.dataclass(frozen=True)
class Move:
    i: int
    j: int


def get_possible_moves(board):
    moves = {}
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == ColorsEnum.FREE:
                moves[Move(i, j)] = True
    moves = list(moves.keys())
    random.shuffle(moves)
    return moves


def get_connected_region(board, i, j):

    board_size = len(board)

    moves = {}
    offsets = [
        (0, -1),
        (0, +1),
        (-1, 0),
        (+1, 0),
        (-1, +1),
        (+1, -1),
    ]
    for offset in offsets:
        offset_factor = 1
        while True:
            new_i = i + offset[0] * offset_factor
            new_j = j + offset[1] * offset_factor
            if new_i >= board_size or new_i < 0 or new_j >= board_size or new_j < 0:
                break
            if board[new_i][new_j] == ColorsEnum.FREE:
                moves[Move(new_i, new_j)] = True

            if offset_factor == ACTIVE_REGION_BOUNDS:
                break

            offset_factor += 1
    return moves


def get_active_moves(board):
    moves = {}
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] != ColorsEnum.FREE:
                moves.update(get_connected_region(board, i, j))
    moves = list(moves.keys())
    random.shuffle(moves)
    return moves
