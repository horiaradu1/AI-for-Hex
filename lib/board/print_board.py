from lib.colors import ColorsEnum


def print_board(board):
    leading_spaces = ""
    for row in board:
        print(leading_spaces, end="")
        for h in row:
            if h == ColorsEnum.RED:
                print(f"\033[1;31mR\033[0m", end=" ")
            if h == ColorsEnum.BLUE:
                print(f"\033[1;34mB\033[0m", end=" ")
            if h == ColorsEnum.FREE:
                print("_", end=" ")
        print()
        leading_spaces += " "
