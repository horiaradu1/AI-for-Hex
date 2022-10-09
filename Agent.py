import socket
from random import choice
from time import sleep
from lib.FSMs_states import StatesEnum
from lib.colors import ColorsEnum, char_to_int_color, get_oposing_color
from lib.minimax.algo import minimax
from lib.board.moves import get_possible_moves, get_active_moves
from lib.board.move_algos import get_active_moves_path
import copy
from lib.board.print_board import print_board
import os
import datetime
from concurrent.futures import ProcessPoolExecutor


class MinMaxAgent:
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234
    SEARCH_DEPTH = 2
    VERBOSE = False
    TIMEOUT_SECONDS = 6
    TIMEOUT_MOVE_SCORE = SEARCH_DEPTH + 3
    SWAP_PROB = 0.85

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """

        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []

        states = {
            StatesEnum.CONNECT: MinMaxAgent._connect,
            StatesEnum.WAIT_START: MinMaxAgent._wait_start,
            StatesEnum.MAKE_MOVE: MinMaxAgent._make_move,
            StatesEnum.WAIT_MESSAGE: MinMaxAgent._wait_message,
            StatesEnum.CLOSE: MinMaxAgent._close,
        }

        res = states[1](self)
        while res != StatesEnum.END:
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((MinMaxAgent.HOST, MinMaxAgent.PORT))

        return StatesEnum.WAIT_START

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if data[0] == "START":
            self._board_size = int(data[1])
            for i in range(self._board_size):
                new_row = []
                for j in range(self._board_size):
                    new_row.append(ColorsEnum.FREE)
                self._board.append(new_row)
            self._colour = data[2]

            if self._colour == "R":
                return StatesEnum.MAKE_MOVE
            else:
                return StatesEnum.WAIT_MESSAGE

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        swap = True
        if self._turn_count == 2:
            if self._board[0][0] != ColorsEnum.FREE:
                swap = False
            elif self._board[len(self._board)-1][len(self._board)-1] != ColorsEnum.FREE:
                swap = False
            elif choice(range(100)) <= 100 - 100*self.SWAP_PROB:
                swap = False

        if self._turn_count == 2 and swap:
            msg = "SWAP\n"
        else:
            start_of_move = datetime.datetime.now()
            moves = get_active_moves_path(self._board)
            # moves = get_active_moves(self._board)
            # moves = []
            best_score = float("-inf")
            best_move = None
            if not moves:
                if self.VERBOSE:
                    print("got all moves")
                moves = get_possible_moves(self._board)

            for move in moves:
                updated_board = copy.deepcopy(self._board)
                updated_board[move.i][move.j] = char_to_int_color(self._colour)
                if self.VERBOSE:
                    print(move.i, move.j)
                score = minimax(
                    updated_board,
                    self.SEARCH_DEPTH,
                    False,
                    char_to_int_color(self._colour),
                    float("-inf"),
                    float("inf"),
                )
                if self.VERBOSE:
                    print(score)

                if datetime.datetime.now() - start_of_move > datetime.timedelta(seconds=self.TIMEOUT_SECONDS):
                    break

                if score == float("inf"):
                    best_move = move
                    self.SEARCH_DEPTH = 1
                    break

                elif score > best_score:
                    best_move = move
                    best_score = score

                elif score > self.TIMEOUT_MOVE_SCORE:
                    best_move = move
                    best_score = score
                    break

            if not best_move:
                best_move = move
            self.TIMEOUT_MOVE_SCORE += 1
            self._board[best_move.i][best_move.j] = char_to_int_color(
                self._colour)
            msg = f"{best_move.i},{best_move.j}\n"

            if self.VERBOSE:
                print(f"Sending message [{msg}]")

        self._s.sendall(bytes(msg, "utf-8"))

        return StatesEnum.WAIT_MESSAGE

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if data[0] == "END" or data[-1] == "END":
            return StatesEnum.CLOSE
        else:

            if data[1] == "SWAP":
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                if self._board[int(x)][int(y)] == ColorsEnum.FREE:
                    self._board[int(x)][int(y)] = char_to_int_color(
                        self.opp_colour())

            if data[-1] == self._colour:
                return StatesEnum.MAKE_MOVE

        return StatesEnum.WAIT_MESSAGE

    def _close(self):
        """Closes the socket."""

        self._s.close()
        return StatesEnum.END

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """

        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"


if __name__ == "__main__":
    agent = MinMaxAgent()
    agent.run()
