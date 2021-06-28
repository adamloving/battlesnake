    function minimax(node, depth, maximizingPlayer) is
        if depth = 0 or node is a terminal node then
            return the heuristic value of node
        if maximizingPlayer then
            value := −∞
            for each child of node do
                value := max(value, minimax(child, depth − 1, FALSE))
            return value
        else (* minimizing player *)
            value := +∞
            for each child of node do
                value := min(value, minimax(child, depth − 1, TRUE))
            return value

Board simulation

- move in each direction (regardless of consequences)
- account for eating/health loss, collisions, hazards

Board Scoring
+1 for health (if still alive). that's it

only works for 1v1 need max^n

could train a random forest on millions of games (given these metrics, and this move, is the outcome improved) - but that's basically reinforcement

Current implementation

- could use current factors to score into the future (make a short tree and pick best) ... just for myself
