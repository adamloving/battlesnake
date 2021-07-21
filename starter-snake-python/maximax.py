

def maximax(board, depth):
    # best = [ None, -1]
    best = [ None, -999]
    total_alive = len(board.board["snakes"])

    if depth == 0 or total_alive <= 1:
        if total_alive == 0:
            is_alive = False
        else:
            is_alive = board.board["snakes"][0]["id"] == board.you_id

        if is_alive and total_alive == 1:
            score = depth # win (high depth better)
        elif is_alive:
            score = 1 - (total_alive - 1) * .25
        else:
            score = -depth # lose (high depth worse)

        # print(f"leaf {depth} {score}")
        return [ None, score]

    # print(f"--- depth {depth} ---")
    scores_by_move = {}
    for board in board.generate():
        my_move = None
        for pnp in board.combo:
            if pnp["is_me"]:
                my_move = pnp["move"]
        if my_move is None: continue

        # print(f"d{depth} Moves: {[pnp['move'] for pnp in board.combo]}")
        [ move, score ] = maximax(board, depth - 1)
        ## print(f"Consider: {board.combo} {[my_move,score]}")

        scores_by_move.setdefault(my_move, [])
        scores_by_move[my_move].append(score)

    for move in scores_by_move:
        avg = sum(scores_by_move[move]) / len(scores_by_move[move])
        if (avg > best[1]):
            best = [move, avg]

    # print(f"scores_by_move {scores_by_move}")
    # print(f"best of depth {depth} {best}")
    return best