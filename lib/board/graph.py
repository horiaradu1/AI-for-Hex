from lib.board.sides import SidesEnum, get_color_for_side
from lib.board.hex import Hex
from lib.board.moves import Move, get_active_moves
from lib.colors import ColorsEnum, get_oposing_color, int_color_to_char
import copy
import queue

from dataclasses import dataclass, field
from typing import Any
import itertools
from heapq import heappop, heappush
from lib.board.moves import Move
import datetime
from collections import defaultdict


class Heap:
    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
        self.REMOVED = '<removed-task>'      # placeholder for a removed task
        self.counter = itertools.count()

    def add_task(self, task, priority=0):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)

    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED
        entry[0] = float("inf")

    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')


class Graph():
    def __init__(self, board, player_color):
        self.board = []
        for i in range(len(board)):
            new_row = []
            for j in range(len(board)):
                new_row.append(Hex(Move(i, j), board[i][j]))
            self.board.append(new_row)

        self.sides = {
            SidesEnum.TOP: Hex(Move(-1, 0), get_color_for_side(SidesEnum.TOP), side=SidesEnum.TOP),
            SidesEnum.BOTTOM: Hex(Move(len(self.board), 0), get_color_for_side(SidesEnum.BOTTOM), side=SidesEnum.BOTTOM),
            SidesEnum.LEFT: Hex(Move(0, -1), get_color_for_side(SidesEnum.LEFT), side=SidesEnum.LEFT),
            SidesEnum.RIGHT: Hex(Move(0, len(self.board)), get_color_for_side(SidesEnum.RIGHT), side=SidesEnum.RIGHT),
        }

        self.set_player_color(player_color)
        self.verbose = False
        self.min_path_distance = float("inf")
        self.board_size = len(board)

    def clear_graph(self):
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                self.board[i][j].distance_from_start = float("inf")

        for key in self.sides.keys():
            self.sides[key].distance_from_start = float("inf")

        self.min_path_distance.distance_from_start = float("inf")

    def get_neighbours(self, piece: Hex):

        if piece.side == SidesEnum.TOP:
            return [self.board[0][j] for j in range(self.board_size)]

        if piece.side == SidesEnum.BOTTOM:
            return [self.board[self.board_size-1][j] for j in range(self.board_size)]

        if piece.side == SidesEnum.LEFT:
            return [self.board[i][0] for i in range(self.board_size)]

        if piece.side == SidesEnum.RIGHT:
            return [self.board[i][len(self.board[0])-1] for i in range(self.board_size)]

        offsets = [
            (0, -1), (0, +1), (-1, 0), (+1, 0), (-1, +1), (+1, -1)
        ]

        neighbours = []

        for offset in offsets:
            new_i = piece.move.i + offset[0]
            new_j = piece.move.j + offset[1]

            if new_i < self.board_size and new_i >= 0 and new_j < self.board_size and new_j >= 0:
                neighbours.append(self.board[new_i][new_j])

            elif new_i == -1:
                neighbours.append(self.sides[SidesEnum.TOP])

            elif new_i == self.board_size:
                neighbours.append(self.sides[SidesEnum.BOTTOM])

            elif new_j == -1:
                neighbours.append(self.sides[SidesEnum.LEFT])

            elif new_j == self.board_size:
                neighbours.append(self.sides[SidesEnum.RIGHT])

        return set(neighbours)

    def get_piece_path_length(self, piece):
        if piece.side:
            return self.sides[piece.side].distance_from_start
        else:
            return self.board[piece.move.i][piece.move.j].distance_from_start

    def update_piece(self, piece):
        if piece.side:
            self.sides[piece.side].distance_from_start = piece.distance_from_start
        else:
            self.board[piece.move.i][piece.move.j].distance_from_start = piece.distance_from_start

    def get_piece_from_move(self, move):
        if move.i in range(len(self.board)) and move.j in range(len(self.board)):
            return self.board[move.i][move.j]
        else:
            if move.i < 0:
                return self.sides[SidesEnum.TOP]
            if move.i >= len(self.board):
                return self.sides[SidesEnum.BOTTOM]
            if move.j < 0:
                return self.sides[SidesEnum.LEFT]
            if move.j >= len(self.board):
                return self.sides[SidesEnum.RIGHT]

    def get_tuple_from_piece(self, piece):
        return (piece.move.i, piece.move.j)

    def make_shortest_path_astar(self, start, end):
        pqueue = Heap()
        pqueue.add_task(start, priority=0)

        predecessors = {}
        visited = defaultdict(lambda: False)

        def heuristic(node):

            if node.side and node.side == end.side:
                return 0

            if node.side:
                return float("inf")

            if end.side == SidesEnum.TOP:
                return node.move.i

            if end.side == SidesEnum.BOTTOM:
                return len(self.board) - node.move.i

            if end.side == SidesEnum.LEFT:
                return node.move.j

            return len(self.board) - node.move.j

        best_path = defaultdict(lambda: float('inf'))
        best_total_guess = defaultdict(lambda: float('inf'))

        best_path[start] = 0
        best_total_guess[start] = heuristic(node=start)

        while True:

            try:
                current = pqueue.pop_task()
            except KeyError:
                break

            if self.verbose:
                print(
                    f"Curent node = [{self.get_tuple_from_piece(current)}] side = [{current.side}]")

            if visited[current]:
                continue
            visited[current] = True

            if self.verbose:
                print(
                    f"Processing node = [{self.get_tuple_from_piece(current)}] side = [{current.side}]")

            if current == end:
                total_path = [end]
                while current in predecessors:
                    current = predecessors[current]
                    total_path.append(current)
                total_path = total_path[::-1]
                return total_path

            for neighbour in self.get_neighbours(current):
                if self.verbose:
                    print(
                        f"Processing neighbour = [{self.get_tuple_from_piece(neighbour)}] side = [{neighbour.side}]")

                if neighbour.color == get_oposing_color(self.player_color):
                    continue

                weight = 0.0 if neighbour.color == self.player_color else 1.0
                tentative_path = best_path[current] + weight

                if tentative_path < best_path[neighbour]:
                    predecessors[neighbour] = current
                    best_path[neighbour] = tentative_path
                    best_total_guess[neighbour] = tentative_path + \
                        heuristic(neighbour)
                    pqueue.add_task(
                        neighbour, priority=best_total_guess[neighbour]
                    )

        return None

    def set_player_color(self, player_color):
        self.player_color = player_color
        self.opponenet_color = get_oposing_color(player_color)

    def make_shortest_path_by_depth(self, current, end, visited, distance=0):

        def heuristic(node, end):

            if node.side and node.side == end.side:
                return 0

            if node.side:
                return float("inf")

            if end.side == SidesEnum.TOP:
                return node.move.i

            if end.side == SidesEnum.BOTTOM:
                return len(self.board) - node.move.i

            if end.side == SidesEnum.LEFT:
                return node.move.j

            return len(self.board) - node.move.j

        if self.verbose:
            print(
                f"\nplace : [{current.move.i}][{current.move.j}] [{current.side}] dist:[{distance}] [{[v for v in visited]}]")

        if current.side == end.side:
            if distance < self.min_path_distance:
                self.min_path_distance = distance
            if self.verbose:
                print("\n return")
            return distance

        if distance > self.min_path_distance:
            return float("inf")

        neighbours = self.get_neighbours(current)
        min_distance = float("inf")

        for neighbour in neighbours:
            if not visited[neighbour.move] and neighbour.color != self.opponenet_color:
                dist_offeset = 0
                if neighbour.color == ColorsEnum.FREE:
                    dist_offeset = 1
                visited[neighbour.move] = True
                new_visited = visited
                min_distance = min(min_distance, self.make_shortest_path_by_depth(
                    neighbour, end, distance=distance+dist_offeset, visited=new_visited))
        return min_distance

        # good_neighbours = Heap()
        # has_unexplored_nodes = False
        # for neighbour in neighbours:
        #     if not visited[neighbour.move] and neighbour.color != self.opponenet_color:
        #         if self.verbose:
        #             print(
        #                 f"Good neighbour [{neighbour.move.i}][{neighbour.move.j}]")

        #         dist_offeset = 0
        #         if neighbour.color == ColorsEnum.FREE:
        #             dist_offeset = 1

        #         heuristic = float("inf")
        #         if neighbour.side and neighbour.side == end.side:
        #             heuristic = float("-inf")

        #         elif end.side == SidesEnum.TOP:
        #             heuristic = neighbour.move.i

        #         elif end.side == SidesEnum.BOTTOM:
        #             heuristic = len(self.board) - neighbour.move.i

        #         elif end.side == SidesEnum.LEFT:
        #             heuristic = neighbour.move.j

        #         elif end.side == SidesEnum.RIGHT:
        #             heuristic = len(self.board) - neighbour.move.j

        #         visited[neighbour.move] = True
        #         has_unexplored_nodes = True
        #         good_neighbours.add_task(
        #             neighbour, heuristic+dist_offeset)

        #     else:
        #         if self.verbose:
        #             print(
        #                 f"Bad neighbour [{neighbour.move.i}][{neighbour.move.j}] color:[{int_color_to_char(neighbour.color)}]")

        # if not has_unexplored_nodes:
        #     return float("inf")

        # while True:
        #     try:
        #         neighbour = good_neighbours.pop_task()
        #     except KeyError:
        #         break

        #     dist_offeset = 0
        #     if neighbour.color == ColorsEnum.FREE:
        #         dist_offeset = 1
        #     new_visited = visited

        #     min_distance = min(min_distance, self.make_shortest_path_by_depth(
        #         neighbour, end, distance=distance+dist_offeset, visited=new_visited))

        # return min_distance

    def make_shortest_path(self, start, end):
        if self.verbose:
            print("\nStarting algo")
        start_algo = datetime.datetime.now()
        current_vertexes = Heap()

        for row in self.board:
            for h in row:
                if h.color == self.player_color or h.color == ColorsEnum.FREE:
                    current_vertexes.add_task(h.move, float("inf"))

        for side in self.sides.values():
            if side.color == self.player_color:
                current_vertexes.add_task(side.move, float("inf"))

        start_vertex = start
        start_vertex.distance_from_start = 0

        current_vertexes.add_task(start.move, 0)

        self.update_piece(start_vertex)

        if self.verbose:
            print(f"Setting up took {datetime.datetime.now() - start_algo}")

        current_vertex = start_vertex
        while True:

            start_loop = datetime.datetime.now()
            try:
                current_vertex = self.get_piece_from_move(
                    current_vertexes.pop_task())
            except KeyError:
                return

            if self.verbose:
                print(
                    f"\nGetting next vertex took {datetime.datetime.now() - start_loop}")

            start_neighbour = datetime.datetime.now()
            neighbours = self.get_neighbours(current_vertex)

            if self.verbose:
                print(
                    f"Got neighbours in {datetime.datetime.now() - start_neighbour}")

            for neighbour in neighbours:
                start_neighbour = datetime.datetime.now()
                if neighbour.move not in current_vertexes.entry_finder:
                    continue
                if neighbour.color == get_oposing_color(self.player_color):
                    current_vertexes.remove_task(neighbour.move)
                    continue

                weight = 0.0 if neighbour.color == self.player_color else 1.0

                new_weight = current_vertex.distance_from_start + weight

                if new_weight < neighbour.distance_from_start:
                    start_update = datetime.datetime.now()

                    current_vertexes.add_task(neighbour.move, new_weight)

                    neighbour.distance_from_start = new_weight

                    self.update_piece(neighbour)

                    if self.verbose:
                        print(
                            f"Updating the neighbour took {datetime.datetime.now() - start_update}")

                    if neighbour.side == end.side:
                        if self.verbose:
                            print(
                                f"\nThe entire algo took {datetime.datetime.now() - start_algo}\n")
                        return
                if self.verbose:
                    print(
                        f"Processing neighbour {neighbour.move.i} {neighbour.move.j} {neighbour.side} took {datetime.datetime.now() - start_neighbour}")

            if self.verbose:
                print(
                    f"Processing one vertex took {datetime.datetime.now() - start_loop}")

            # if current_vertexes.empty():
            #     return
