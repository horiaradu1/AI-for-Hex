from lib.board.graph import Graph
from lib.colors import ColorsEnum
from lib.board.sides import get_sides_for_color
from lib.board.moves import Move
from collections import defaultdict
import random

ACTIVE_REGION_BOUNDS = 1


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


def get_active_moves_path(board):
    graph = Graph(board, ColorsEnum.RED)

    player_sides = get_sides_for_color(ColorsEnum.RED)
    red_path = graph.make_shortest_path_astar(
        graph.sides[player_sides[1]], graph.sides[player_sides[0]])

    player_sides = get_sides_for_color(ColorsEnum.BLUE)
    graph.set_player_color(ColorsEnum.BLUE)
    blue_path = graph.make_shortest_path_astar(
        graph.sides[player_sides[1]], graph.sides[player_sides[0]])
    interesting_moves = defaultdict(lambda: False)
    if blue_path:
        for node in blue_path:
            if not node.side and node.color == ColorsEnum.FREE and not interesting_moves[node.move]:
                interesting_moves[node.move] = True
    if red_path:
        for node in red_path:
            if not node.side and node.color == ColorsEnum.FREE and not interesting_moves[node.move]:
                interesting_moves[node.move] = True

    interesting_moves = list(interesting_moves.keys())
    random.shuffle(interesting_moves)
    return interesting_moves
