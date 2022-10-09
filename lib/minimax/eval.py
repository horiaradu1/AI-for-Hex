import random
from lib.board.graph import Graph
from lib.board.sides import get_sides_for_color
from lib.colors import ColorsEnum, get_oposing_color, int_color_to_char
from lib.board.print_board import print_board
from collections import defaultdict

board_states = {}
verbose = False


def collapse_board(board):
    collaped = ""
    for row in board:
        for h in row:
            collaped += int_color_to_char(h)
    return collaped


def get_score(graph, board, player_color):
    player_sides = get_sides_for_color(player_color)
    if verbose:
        print()
        print(player_color)
        print(player_sides)

    # graph.make_shortest_path(
    #     graph.sides[player_sides[1]], graph.sides[player_sides[0]]
    # )
    # shortest_path = graph.sides[player_sides[0]].distance_from_start

    # return shortest_path - 1

    visited = defaultdict(lambda: False)
    visited[graph.sides[player_sides[1]].move] = True
    length = graph.make_shortest_path_by_depth(
        graph.sides[player_sides[1]], graph.sides[player_sides[0]], visited=visited)
    if verbose:
        print(
            f"Path length for {int_color_to_char(graph.player_color)} {length}")
    return length

    # path = graph.make_shortest_path_astar(
    #     graph.sides[player_sides[1]], graph.sides[player_sides[0]])

    # if not path:
    #     return float("inf")

    # moves_to_complete = 0
    # for hax in path:
    #     if hax.color == ColorsEnum.FREE:
    #         moves_to_complete += 1
    #         # print("Hello Horia!")

    # return moves_to_complete


def evaluation(board, player_color):
    if verbose:
        print("BEGIN EVAL")
        print(player_color)
        print_board(board)

    global board_states
    collapsed_board = collapse_board(board)

    if collapsed_board in board_states:
        if verbose:
            print("\nused cached board\n")
        return board_states[collapsed_board]

    game_graph = Graph(board, player_color)

    player_score = get_score(game_graph, board, player_color)

    # game_graph.clear_graph()
    game_graph.min_path_distance = float("inf")

    oposing_color = get_oposing_color(player_color)

    game_graph.set_player_color(oposing_color)

    oposing_score = get_score(game_graph, board, oposing_color)

    del game_graph

    if verbose:
        print(oposing_score - player_score)
        print(f"BOARD SCORE {oposing_score - player_score}")

    board_states[collapsed_board] = oposing_score - player_score

    return oposing_score - player_score
