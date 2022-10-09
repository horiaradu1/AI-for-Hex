from lib.minimax.eval import evaluation, board_states, collapse_board
from lib.board.moves import get_possible_moves, get_active_moves
from lib.board.move_algos import get_active_moves_path
import copy
from lib.colors import get_oposing_color


def minimax(board, depth, isMaximizingPlayer, maximixing_color, alpha, beta):
    if depth == 0:
        return evaluation(copy.deepcopy(board), maximixing_color)

    # moves = get_active_moves(board)
    # moves = get_possible_moves(board)
    moves = get_active_moves_path(copy.deepcopy(board))

    if moves:
        if isMaximizingPlayer:
            bestValue = float("-inf")
            for move in moves:
                updated_board = copy.deepcopy(board)
                updated_board[move.i][move.j] = maximixing_color
                bestValue = max(
                    bestValue,
                    minimax(
                        updated_board, depth - 1, False, maximixing_color, alpha, beta
                    ),
                )
                if bestValue >= beta:
                    break
                alpha = max(alpha, bestValue)

            return bestValue
        else:
            bestValue = float("inf")
            opponent_color = get_oposing_color(maximixing_color)
            for move in moves:
                updated_board = copy.deepcopy(board)
                updated_board[move.i][move.j] = opponent_color
                bestValue = min(
                    bestValue,
                    minimax(
                        updated_board, depth - 1, True, maximixing_color, alpha, beta
                    ),
                )
                if bestValue <= alpha:
                    break
                beta = min(beta, bestValue)

            return bestValue
    else:
        return evaluation(board, maximixing_color)
