import copy
import itertools

DIRECTIONS = directions = ["up", "down", "left", "right"]

class Board(object):

    def __init__(self, board = {
        "height": 11,
        "width": 11,
        "snakes": [],
        "food": [],
        "hazards": []
    }, you_id = ""):
        self.board = board
        self.size = self.board["width"]
        self.matrix = self.get_matrix()
        self.you_id = you_id

        # preserve this collection and remove killed snakes from board["snakes"]
        self.snakes_by_id = {}
        for snake in self.board["snakes"]:
            self.snakes_by_id[snake["id"]] = snake

    def get_matrix(self):
        # initialize a list of lists
        matrix = [[" " for x in range(self.size)] for y in range(self.size)]

        # This should mark the food in the board
        for food in self.board["food"]:
          for food_position in self.board["food"]:
            matrix[food_position["x"]][food_position["y"]] = "F"

        for hazard in self.board["hazards"]:
          for hazard_position in self.board["hazards"]:
            matrix[hazard_position["x"]][hazard_position["y"]] = "H"

        # mark where the snakes are
        for snake in self.board["snakes"]:
            for body_position in snake["body"]:
                matrix[body_position["x"]][body_position["y"]] = f"S:{snake['id']}"

        return matrix

    def print(self):
        size = len(self.matrix)
        print("")
        for y in reversed(range(size)):
            print(" | ", end='')
            for x in range(size):
                id = self.matrix[x][y]
                if len(id) > 1:
                    id = id[2:3]
                print(f"{id}", end='')
                print(" | ", end='')
            print("")
        print("")

    # generate all combinations of valid possible next positions
    def generate_pnp_combos(self):
        all_pnps = []
        my_head = self.snakes_by_id[self.you_id]["head"]

        for snake in self.board["snakes"]:
            is_me = snake["id"] == self.you_id

            if not is_me and self.get_distance(my_head, snake["head"]) >= 3:
                print(f"ignore far away {snake['id']}")
                continue # ignore distant snakes

            pnps = [] # possible next positions
            for move in DIRECTIONS:
                next_position = self.get_next_position(snake["head"], move)
                if not self.is_on_board(next_position): continue
                if self.is_occupied(next_position): continue
                
                print(f"possible move: {snake['id']} {move} {next_position}")
                pnps.append({
                    "id": snake["id"],
                    "move": move,
                    "is_me":  is_me,
                    "position": next_position
                })
            all_pnps.append(pnps)

        return list(itertools.product(*all_pnps))



    # generate possible next boards
    def generate(self):
        boards = []
        combos = self.generate_pnp_combos()
        print(f"Combos: {len(combos)}")

        # resolve conflicts
        for combo in combos:
            # print("--- START ---")
            new_board = Board(copy.deepcopy(self.board), self.you_id)
            # new_board.print()
            new_board.combo = combo
            for pnp in combo:
                # print("pnp ---")
                p = pnp["position"]
                current_snake = new_board.snakes_by_id[pnp["id"]]
                occupant = new_board.matrix[p["x"]][p["y"]]

                if occupant == " ":
                    #print(f"No occupant {p}")
                    new_board.move_snake(pnp["id"], p)
                    # new_board.debuglog.push(f"{pnp['id']} moved pnp['move']")
                elif occupant[0] == "S":
                    #print(f"Other snake {p} {occupant}")
                    occupant_id = occupant[2:]
                    occupant_snake = new_board.snakes_by_id[occupant_id]

                    if occupant_snake["head"] == p:
                        if occupant_snake["length"] > current_snake["length"]:
                            new_board.kill_snake(current_snake["id"])
                        elif occupant_snake["length"] < current_snake["length"]:
                            new_board.kill_snake(occupant_snake["id"])
                            new_board.move_snake(current_snake["id"], p)
                        else:
                            #print("same length")
                            # bugbug should be a 50/50 case
                            new_board.kill_snake(current_snake["id"])
                    else:
                        print(f"wtf {pnp} >{occupant}<")
                        # new_board.print()
                        #print(current_snake)
                        #print(occupant_snake)
                        # I ran into someone (this shouldn't happen)
                        new_board.kill_snake(current_snake["id"])

                else: # ignore food or hazard
                    # print(f"food or hazard at {p}")
                    new_board.move_snake(current_snake["id"], p)
            
            # print(combo)
            # print('\x1bc')
            # new_board.print()
            boards.append(new_board)

        return boards

    def kill_snake(self, id):
        #print(f"kill {id}")
        snake = self.snakes_by_id[id]
        for position in snake["body"]:
            self.matrix[position["x"]][position["y"]] = " "
        self.board["snakes"] = [snake for snake in self.board["snakes"] if snake["id"] != id]
        self.snakes_by_id.pop(id, None) # remove from dict

    # todo eval food
    def move_snake(self, id, p):
        snake = self.snakes_by_id[id]
        marker = f"S:{id}"

        # remove and ignore food and hazards
        occupant = self.matrix[p["x"]][p["y"]]
        if occupant == "F": self.board["food"].remove(p)
        if occupant == "H": self.board["hazards"].remove(p)

        snake["head"] = p
        snake["body"].insert(0, p)
        tail = snake["body"].pop()

        self.matrix[p["x"]][p["y"]] = marker
        self.matrix[tail["x"]][tail["y"]] = " "
        

    # translate move into position (without bounds check)
    def get_next_position(self, current_position, direction):
        new_position = {
          "x": current_position["x"], "y": current_position["y"]
        }
        if direction == "up":
            new_position["y"] = new_position["y"] + 1
        elif direction == "down":
            new_position["y"] = new_position["y"] - 1
        elif direction == "right":
            new_position["x"] = new_position["x"] + 1
        elif direction == "left":
            new_position["x"] = new_position["x"] - 1

        return new_position

    def is_on_board(self, position):
      if position["x"] < 0:
        return False
      if position["y"] < 0:
        return False
      if position["x"] > self.size - 1:
        return False
      if position["y"] > self.size - 1:
        return False

      return True

    def is_occupied(self, position):
        return self.matrix[position['x']][position['y']][0] == "S"

    def get_distance(self, p1, p2):
      dist_x = abs(p1["x"] - p2["x"])
      dist_y = abs(p1["y"] - p2["y"])
      # print(f"dist: {p1} -> {p2} = {dist_x} + {dist_y}")
      return dist_x + dist_y

    def score_for_current_player(self):
        total_alive = len(self.board["snakes"])

        if total_alive == 0: return 0

        is_alive = False
        for snake in self.board["snakes"]:
            is_alive = snake["id"] == self.you_id
            if is_alive: break
        
        if not is_alive: return 0 # lose!
        
        others_penalty = (total_alive - 1) * .25

        hazard_penalty = 0
        me = self.snakes_by_id[self.you_id]
        if me["head"] in self.board["hazards"]:
            hazard_penalty = 0.5
    
        if is_alive and total_alive == 1: return 1 # win!

        return max(0, 1 - others_penalty - hazard_penalty)

    def score_for_others(self):
        total_alive = len(self.board["snakes"])

        if total_alive == 0:
            return 0 # everybody dead

        is_you_alive = False
        for snake in self.board["snakes"]:
            is_you_alive = snake["id"] == self.you_id
            if is_you_alive: break 
        
        if not is_you_alive: return 1 # we killed him

        return (total_alive - 1) * .25
