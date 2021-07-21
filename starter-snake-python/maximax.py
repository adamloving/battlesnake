

def maximax(board, depth):
    best = [ None, None, None, {}, {}]
    total_alive = len(board.board["snakes"])

    if depth == 0 or total_alive <= 1:
        if total_alive == 0:
            is_alive = False
        else:
            is_alive = board.board["snakes"][0]["id"] == board.you_id

        if is_alive and total_alive == 1:
            score = depth # win (high depth = sooner, better)
            other_score = -depth
        elif is_alive: # multiple alive
            score = 1 - (total_alive - 1) * .25
            other_score = (total_alive - 1) * .25
        else:
            score = -depth # lose (high depth = sooner, worse)
            other_score = depth

        # discount hazard
        me = board.snakes_by_id[board.you_id]
        if me["head"] in board.board["hazards"]:
            score = score - 0.5

        # print(f"leaf {depth} {score}")
        return [ None, score, other_score, {}, {}]

    # print(f"--- depth {depth} ---")
    scores_by_move = {}
    scores_by_move_other = {}
    best_move = None
    for board in board.generate():
        my_move = None
        for pnp in board.combo:
            if pnp["is_me"]:
                my_move = pnp["move"]
        if my_move is None: continue

        # print(f"d{depth} Moves: {[pnp['move'] for pnp in board.combo]}")
        [ move, score, other_score, sbm, sbm_other ] = maximax(board, depth - 1)
        # print(f"{[ move, score, other_score, sbm, sbm_other ]}")

        # pick best move for me with best move for other guy
        scores_by_move.setdefault(my_move, -9999)
        scores_by_move_other.setdefault(my_move, -9999)

        if score > scores_by_move[my_move] and other_score > scores_by_move_other[my_move]:
            best_move = my_move
            scores_by_move[my_move] = score
            scores_by_move_other[my_move] = other_score

    # print(f"{depth}: scores_by_move {scores_by_move} {scores_by_move_other}")
    # print(f"best of depth {depth} {best}")
    return [ best_move, scores_by_move[best_move], scores_by_move_other[best_move], scores_by_move, scores_by_move_other]