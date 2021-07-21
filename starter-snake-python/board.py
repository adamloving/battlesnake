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

    # generate possible next boards
    def generate(self):
        boards = []
        all_pnps = []
        my_head = self.snakes_by_id[self.you_id]["head"]

        for i, snake in enumerate(self.board["snakes"]):
            is_me = snake["id"] == self.you_id

            if not is_me and self.get_distance(my_head, snake["head"]) >= 3:
                # print(f"ignore far away {snake['id']}")
                continue # ignore distant snakes

            pnps = [] # possible next positions
            for move in DIRECTIONS:
                next_position = self.get_next_position(snake["head"], move)
                if not self.is_on_board(next_position): continue
                if self.matrix[next_position['x']][next_position['y']][0] == "S": continue
                # print(f"np: {snake['id']} {move} {next_position}")
                pnps.append({ 
                    "id": snake["id"],
                    "move": move, 
                    "is_me":  is_me,
                    "position": next_position
                })
            all_pnps.append(pnps)
        
        combos = list(itertools.product(*all_pnps))

        #print("####")
        #[print(len(pnps)) for pnps in all_pnps]
        print(f"Combos: {len(combos)}")

        # resolve conflicts
        for combo in combos:            
            # print("NEXT COMBO")
            # self.print()
            new_board = Board(copy.deepcopy(self.board), self.you_id)
            new_board.combo = combo
            for pnp in combo:
                p = pnp["position"]
                # print(f"pnp: {pnp}")
                marker = f"S:{pnp['id']}"
                current_snake = new_board.snakes_by_id[pnp["id"]]
                occupant = new_board.matrix[p["x"]][p["y"]]
                
                if occupant == " ":
                    #print(f"No occupant {p} {marker}")
                    new_board.matrix[p["x"]][p["y"]] = marker
                    current_snake["body"].insert(0, p)
                    current_snake["head"] = p
                elif occupant[0] == "S":
                    #print(f"Other snake {p} {occupant}")
                    occupant_id = occupant[2:]
                    occupant_snake = new_board.snakes_by_id[occupant_id]

                    if occupant_snake["head"] == p:                        
                        if occupant_snake["length"] > current_snake["length"]:
                            new_board.kill_snake(current_snake["id"])
                        elif occupant_snake["length"] < current_snake["length"]:
                            new_board.kill_snake(occupant_snake["id"])
                            new_board.matrix[p["x"]][p["y"]] = marker
                            current_snake["body"].insert(0, p)
                            current_snake["head"] = p
                        else:
                            #print("same length")
                            # bugbug should be a 50/50 case
                            new_board.kill_snake(current_snake["id"])
                    else:
                        #print("wtf")
                        #print(current_snake)
                        #print(occupant_snake)
                        # I ran into someone (this shouldn't happen)
                        new_board.kill_snake(current_snake["id"])

                else: # ignore food or hazard
                    # print(f"food or hazard at {p}")
                    new_board.matrix[p["x"]][p["y"]] = marker
                    current_snake["body"].insert(0, p)
                    current_snake["head"] = p
                    # bugbug: remove from board["food"] and board["hazards"]
                
                    
            # todo: eval food and move tails        
            # print(combo)
            # print('\x1bc')
            # new_board.print()
            boards.append(new_board)
                
        return boards

    def kill_snake(self, id):
        # print(f"kill {id}")
        snake = self.snakes_by_id[id]
        for position in snake["body"]:
            self.matrix[position["x"]][position["y"]] = " "
        self.board["snakes"] = [snake for snake in self.board["snakes"] if snake["id"] != id]


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

    def get_distance(self, p1, p2):
      dist_x = abs(p1["x"] - p2["x"])
      dist_y = abs(p1["y"] - p2["y"])
      # print(f"dist: {p1} -> {p2} = {dist_x} + {dist_y}")
      return dist_x + dist_y