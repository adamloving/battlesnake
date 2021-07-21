

def maximax(board, depth):
    # best = [ None, -1]
    best = [ None, -1]
    total_alive = len(board.board["snakes"])

    if depth == 0 or total_alive <= 1:
        if total_alive == 0:
            is_alive = False
        else:
            is_alive = board.board["snakes"][0]["id"] == board.you_id
    
        if is_alive:
            score = 1 - (total_alive - 1) * .25
        else:
            score = -1
            
        print(f"leaf {depth} {score}")
        return [ None, score]

    print(f"--- depth {depth} ---")
    for board in board.generate():
        my_move = None
        for pnp in board.combo:
            if pnp["is_me"]:
                my_move = pnp["move"]
        if my_move is None: continue

        [ move, score ] = maximax(board, depth - 1)
        
        if score > best[1]:
            best = [ my_move, score ]
        
    print(f"best of depth {depth} {best}")
    return best