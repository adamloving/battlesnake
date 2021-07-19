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
        
    def get_matrix(self): 
        # initialize a list of lists
        matrix = [[" " for x in range(self.size)] for y in range(self.size)]

        # mark where the snakes are
        for snake in self.board["snakes"]:
            for body_position in snake["body"]:
                matrix[body_position["x"]][body_position["y"]] = f"S:{snake['id']}"

        # This should mark the food in the board
        for food in self.board["food"]:
          for food_position in self.board["food"]:
            matrix[food_position["x"]][food_position["y"]] = "F"

        for hazard in self.board["hazards"]:
          for hazard_position in self.board["hazards"]:
            matrix[hazard_position["x"]][hazard_position["y"]] = "H"

        return matrix
    
    def print(self):
        size = len(self.matrix)
        print("")
        for y in reversed(range(size)):
            print(" | ", end='')
            for x in range(size):
                print(f"{self.matrix[x][y][0]}", end='')
                print(" | ", end='')
            print("")
        print("")

    # generate possible next boards
    def generate(self):
        boards = []
        all_pnps = []

        for i, snake in enumerate(self.board["snakes"]):
            is_me = snake["id"] == self.you_id
            pnps = [] # possible next positions
            for move in DIRECTIONS:
                next_position = self.get_next_position(snake["head"], move)
                if not self.is_on_board(next_position): continue
                if next_position in snake["body"]: continue
                pnps.append({ 
                    "index": i,
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
            new_board = Board(self.board.copy(), self.you_id)
            new_board.combo = combo
            for pnp in combo:
                p = pnp["position"]
                marker = f"S:{snake['id']}"
                current_snake_index =  pnp["index"]
                current_snake = new_board.board["snakes"][current_snake_index]
                #print(f"current_snake: {current_snake}")
                occupant = new_board.matrix[p["x"]][p["y"]]
                
                if occupant == " ":
                    #print(f"No occupant {p} {marker}")
                    new_board.matrix[p["x"]][p["y"]] = marker
                else:
                    if occupant[0] == "S":
                        occupant_id = occupant[2:]
                        print(f"o_id: >{occupant_id}<")
                        occupant_snake = self.get_snake_by_id(occupant_id)
                        if occupant_snake["length"] > current_snake["length"]:
                            new_board.kill_snake(current_snake["id"])
                        else:
                            new_board.kill_snake(occupant_snake["id"])
                    
            # todo: eval food and move tails        
            # print(combo)
            # new_board.print()
            boards.append(new_board)
                
        return boards

    def get_snake_by_id(self, id):
        for snake in self.board["snakes"]:
            print(snake["id"])
            if snake["id"] == id: 
                return snake
        raise Exception(f"Snake not found {id}")

    def kill_snake(self, id):
        snake = self.get_snake_by_id(id)
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

