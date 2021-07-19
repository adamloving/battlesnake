

def maximax(board, depth):
    best = [ None, -1]
    if depth == 0 or len(board.board["snakes"]) == 1:
        is_alive = board.board["snakes"][0]["id"] == board.you_id
        score = 1 if is_alive else -1
        print(f"leaf {score}")
        return [ None, score]

    for board in board.generate():
        for pnp in board.combo:
            if pnp["is_me"]:
                current_move = pnp["move"]

        [ move, score ] = maximax(board, depth - 1)

        if score > best[1]:
            best = [ current_move, score ]
            
    print(f"best of depth {depth} {[move, score]}")
    return best