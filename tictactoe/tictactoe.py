"""
Tic Tac Toe Player
"""
import copy

X = "X"
O = "O"
EMPTY = None


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
    if board == initial_state():
        return X

    x_count = 0
    o_count = 0

    # count how many turns each player has played
    for row in board:
        for player in row:
            if player == X:
                x_count += 1
            elif player == O:
                o_count += 1

    if x_count > o_count:
        return O

    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    actions = set()

    # actions are all the EMPTY cells in the board
    for i, row in enumerate(board):
        for j, each in enumerate(row):
            if each == EMPTY:  # if a cell is EMPTY, we can make a move there
                actions.add((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    i = action[0]
    j = action[1]

    if not (0 <= i < 3 and 0 <= j < 3):  # negative out-of-bound checking
        raise Exception("Invalid action.")
    if board[i][j] != EMPTY:
        raise Exception("Invalid action.")

    current_player = player(board)

    new_board = copy.deepcopy(board)

    new_board[action[0]][action[1]] = current_player

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # horizontal check
    for row in range(0, 3):
        if board[row][0] == board[row][1] == board[row][2] != EMPTY:
            return board[row][0]

    # vertical check
    for col in range(0, 3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]

    # diagonal top-left to bottom-right

    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]

    # diagonal top-right to bottom-left
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]

    return None  # if no winner


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # if there's a winner, terminal!
    if winner(board):
        return True

    # if moves available, not terminal!
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
    """
    Returns the optimal action for the current player on the board.
    """

    # no actions if the board is terminal
    if terminal(board):
        return None

    current_player = player(board)
    possible_actions = actions(board)
    best_score = -999 if current_player == X else 999

    opt_action = None

    # go thru each possible action for current board
    for action in possible_actions:
        current_board = result(board, action)
        score = minimax_value(current_board)  # calculate score the current action

        if current_player == X:
            if score > best_score:
                best_score = score
                opt_action = action

        else:
            if score < best_score:
                best_score = score
                opt_action = action

    return opt_action


def minimax_value(board):
    """
    Returns the best score of the current board for the current player
    """

    if terminal(board):
        return utility(board)

    current_player = player(board)
    possible_actions = actions(board)
    best_score = -999 if current_player == X else 999

    for action in possible_actions:
        current_board = result(board, action)

        score = minimax_value(current_board)  # recursive call

        if current_player == X:
            if score > best_score:
                best_score = score
        else:
            if score < best_score:
                best_score = score

    return best_score
