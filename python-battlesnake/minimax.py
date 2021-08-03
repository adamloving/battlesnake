
# this is not tested to be working yet
def minimax(board, depth, is_you = True):
    best = None
    total_alive = len(board.board["snakes"])
    is_alive = board.you_id in board.snakes_by_id

    if depth <= 0 or total_alive <=1 or not is_alive:
        if is_you: 
            # print(f"leaf me")
            # board.print()
            # print(board.score_for_current_player())
            return [None, board.score_for_current_player()]
        else: 
            # print(f"leaf other")
            # board.print()
            # print(board.score_for_others())
            return [None, board.score_for_others()]

    if is_you:
        value = -9999
        for child in board.generate():
            [ignore, child_value] = minimax(child, depth - 1, False)
            if child_value > value:
                best = child.you_move
                value = child_value

        # print(f"{depth} Best for me: {best} {value}")
        return [best, value]

    else: 
        value = 9999
        for child in board.generate():
            [ignore, child_value] = minimax(child, depth - 1, True)
            if child_value < value:
                best = child.you_move
                value = child_value
        
        # print(f"{depth} Best for them: me:{best} {value}")
        return [best, value]
