"""
Tic Tac Toe Player
"""

import math
from random import randint
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X
    num_of_X = 0
    num_of_O = 0
    for row in board:
        for cell in row:
            if cell == X:
                num_of_X += 1
            elif cell == O:
                num_of_O += 1
    if num_of_X > num_of_O:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    candidates = set()
    for row_num, row in enumerate(board):
        for cell_num, cell in enumerate(row):
            if cell == EMPTY:
                candidates.add((row_num, cell_num))
    return candidates


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board_copy = deepcopy(board)
    try:
        row, cell = action
        board_copy[row][cell] = player(board)
        return board_copy
    except ValueError:
        print("Action is invalid")


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Checks if X won
    if (
        (board[0][0] == X and board[0][1] == X and board[0][2] == X)  # Across the top
        # Across the middle
        or (board[1][0] == X and board[1][1] == X and board[1][2] == X)
        # Across the bottom
        or (board[2][0] == X and board[2][1] == X and board[2][2] == X)
        # Down the left side
        or (board[0][0] == X and board[1][0] == X and board[2][0] == X)
        # Down the middle
        or (board[0][1] == X and board[1][1] == X and board[2][1] == X)
        # Down the right
        or (board[0][2] == X and board[1][2] == X and board[2][2] == X)
        # Diagonal
        or (board[0][0] == X and board[1][1] == X and board[2][2] == X)
        # Diagonal
        or (board[0][2] == X and board[1][1] == X and board[2][0] == X)
    ):
        return X

    # Checks if O won
    elif (
        (board[0][0] == O and board[0][1] == O and board[0][2] == O)  # Across the top
        # Across the middle
        or (board[1][0] == O and board[1][1] == O and board[1][2] == O)
        # Across the bottom
        or (board[2][0] == O and board[2][1] == O and board[2][2] == O)
        # Down the left side
        or (board[0][0] == O and board[1][0] == O and board[2][0] == O)
        # Down the middle
        or (board[0][1] == O and board[1][1] == O and board[2][1] == O)
        # Down the right
        or (board[0][2] == O and board[1][2] == O and board[2][1] == O)
        # Diagonal
        or (board[0][0] == O and board[1][1] == O and board[2][2] == O)
        or (board[0][2] == O and board[1][1] == O and board[2][0] == O)
    ):  # Diagonal )
        return O

    # Returns None if no winner
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Checks if ther is already a winner
    if winner(board):
        return True

    # Checks if board has any more empty cells
    check = []
    for row in board:
        for cell in row:
            check.append(cell)
    if EMPTY not in check:
        return True

    # If no winner and board is not completely filled, returns False
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    result = winner(board)
    if result == X:
        return 1
    elif result == O:
        return -1
    elif terminal(board):
        return 0


def max_value(board, alpha=-math.inf, beta=math.inf):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max((v, min_value(result(board, action), alpha, beta)))

        if v >= beta:
            return v
        if v > alpha:
            alpha = v
    return v


def min_value(board, alpha=-math.inf, beta=math.inf):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action), alpha, beta))

        if v <= alpha:
            return v
        if v < beta:
            beta = v
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Checks if board is terminal and return None if it is
    if terminal(board):
        return None

    # Choose a random starting position if board is empty (For optimization purpose)
    elif board == initial_state():
        action = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]
        random_num = randint(0, 4)
        return action[random_num]

    if player(board) == X:
        best = -math.inf
        actions_playable = [best, None]
        for action in actions(board):
            best = max(best, min_value(result(board, action)))
            if best > actions_playable[0]:
                actions_playable[0] = best
                actions_playable[1] = action
        return actions_playable[1]

    else:
        best = math.inf
        actions_playable = [best, None]
        for action in actions(board):
            best = min(best, max_value(result(board, action)))
            if best < actions_playable[0]:
                actions_playable[0] = best
                actions_playable[1] = action
        return actions_playable[1]
