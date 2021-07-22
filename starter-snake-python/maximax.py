
def by_average_desc(choice):
    return - choice[1]

def maximax(board, depth):
    total_alive = len(board.board["snakes"])
    is_alive = board.you_id in board.snakes_by_id

    if depth == 0 or total_alive <= 1 or not is_alive:
        you_score = board.score_for_current_player()
        other_score = board.score_for_others()

        print(f"leaf d:{depth} you: {you_score} others: {other_score}")
        return [ None, you_score - other_score, {}]

    print(f"--- depth {depth} ---")
    dbm = {} # delta by move
    for board in board.generate():
        for pnp in board.combo:
            if pnp["is_me"]:
                my_move = pnp["move"]
        if my_move is None: continue # unexpected
        dbm.setdefault(my_move, [])

        # can't do delta or average because need min and max
        # of the ones that have the best value for other, which has the best value for me

        [ ignore, delta, ignore_cdbm] = maximax(board, depth - 1)

        dbm[my_move].append(delta)

    choices = []
    for move in dbm:
        average = sum(dbm[move]) / len(dbm[move])
        dbm[move] = average
        choices.append([ move, average])

    print(f"maximax choices {choices}")

    if len(choices) > 0:
        choices.sort(key=by_average_desc)
        best_move = choices[0][0]
        average = choices[0][1]
    else:
        best_move = None
        average = -1 # must've been no pnps including me

    # print(f"{depth}: scores_by_move {scores_by_move} {scores_by_move_other}")
    # print(f"best of depth {depth} {best}")
    return [ best_move, average, dbm ]