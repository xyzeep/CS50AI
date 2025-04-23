"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None
FIRST_MOVER = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    if terminal(board):
        return None

    count_X = sum(row.count('X') for row in board)
    count_O = sum(row.count('O') for row in board)

    return X if count_X == count_O else O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    for i, row in enumerate(board):
        for j, each in enumerate(row):
            if each == EMPTY:
                possible_actions.add((i, j))  # coordinates of empty cells

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    i = action[0]
    j = action[1]
    if i < 0 or i > 2 or j < 0 or j > 2:
        raise Exception("Invalid action: index out of bounds")
    if board[i][j] == EMPTY:
        new_board[i][j] = player(board) # fill that space with current player
    else:
        raise Exception("Invalid action: cannot move on already filled cell")

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            if board[i][0] != None:
                return board[i][0]

    # columns
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            if board[0][i] != None:
                return board[0][i]

    # diagonals
    if (board[0][0] == board[1][1] == board[2][2]) or (board[2][0] == board[1][1] == board[0][2]):
        if board[1][1] != None:
            return board[1][1]

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == None:
        for row in board:
            for each in row:
                if each == EMPTY:
                    return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0


def minimax(board):
    if terminal(board):
        return None

    current_player = player(board)
    best_score = float('-inf') if current_player == X else float('inf')
    best_move = None

    for action in actions(board):
        current_board = result(board, action)
        score = minimax_value(current_board)  # recursive call

        if current_player == X:
            if score > best_score:
                best_score = score
                best_move = action
        else:
            if score < best_score:
                best_score = score
                best_move = action

    return best_move

def minimax_value(board):
    if terminal(board):
        return utility(board)

    current_player = player(board)
    best_score = float('-inf') if current_player == X else float('inf')
    best_move = None

    for action in actions(board):
        current_board = result(board, action)
        score = minimax_value(current_board)

        if current_player == X:
            if score > best_score:
                best_score = score
                best_move = action
        else:
            if score < best_score:
                best_score = score
                best_move = action

    return best_score



