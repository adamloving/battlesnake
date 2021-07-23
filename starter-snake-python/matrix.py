DIRECTIONS = directions = ["up", "down", "left", "right"]

class Matrix(object):

    def __init__(self, board = {
        "height": 11,
        "width": 11,
        "snakes": [],
        "food": [],
        "hazards": []
    }, p = {"x": 0, "y": 0}):

        self.board = board
        self.size = self.board["width"]
        self.p = p
        self.init_matrix()

        # preserve this collection and remove killed snakes from board["snakes"]
        self.snakes_by_id = {}
        for snake in self.board["snakes"]:
            self.snakes_by_id[snake["id"]] = snake

    def at(self, p):
        return self.matrix[p["x"]][p["y"]]

    def init_matrix(self):
        # initialize a list of lists
        self.matrix = [[[None] * 6 for x in range(self.size)] for y in range(self.size)]

        for food in self.board["food"]:
          for p in self.board["food"]:
            self.at(p)[0] = "F"

        for hazard in self.board["hazards"]:
          for p in self.board["hazards"]:
            self.at(p)[0] = "H"

        # mark where the snakes are
        for snake in self.board["snakes"]:
            for p in snake["body"]:
                self.at(p)[0] = f"S:{snake['id']}"

        # self.fill_distance_around([self.p])
        self.count_flood_fill(self.p)

    # breadth first distance from p
    def fill_distance_around(self, q, depth = 0):
        max_depth = depth
        if len(q) == 0: return max_depth
        else:
            children = []
            for p in q:
                self.at(p)[1] = depth       
                neighbors = self.get_unvisited_neighbors(p, 1)
                print(f"{depth} {max_depth} {p} {neighbors}")
                for n in neighbors:
                    if not n in children: children.append(n)

            max_depth = self.fill_distance_around(children, depth + 1)
            # print(f"> {depth} {max_depth}")
            # if depth > 0:
            #     for p in q:
            #         self.at(p)[2] = max_depth

            return max_depth

    # depth first max depth
    # bugbug: max depth not propagated down short branches 
    # (or neighboring space may be part of separate short branches)
    def count_flood_fill(self, p):
        count = 0
        if not self.is_on_board(p): return count
        if self.at(p)[2] is not None: return count
        if self.is_occupied(p): return count

        count = 1
        self.at(p)[2] = count
        count += self.count_flood_fill({"x": p["x"] - 1, "y": p["y"] })
        count += self.count_flood_fill({"x": p["x"] + 1, "y": p["y"] })
        count += self.count_flood_fill({"x": p["x"], "y": p["y"] - 1})
        count += self.count_flood_fill({"x": p["x"], "y": p["y"] + 1})

        self.at(p)[2] = count
        return count

    def get_unvisited_neighbors(self, p, dimension = 1):
        open_neighbors = []
        for move in DIRECTIONS:
            n = self.get_next_position(p, move)
            if not self.is_on_board(n): continue
            if self.is_occupied(n): continue
            if self.at(n)[dimension] is not None: continue
            open_neighbors.append(n)
        return open_neighbors

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

    def is_occupied(self, p):
        marker = self.at(p)[0]
        return marker is not None and marker[0] == "S"

    def print(self, dimension = 0):
        size = len(self.matrix)
        print("")
        for y in reversed(range(size)):
            print(" | ", end='')
            for x in range(size):
                id = self.matrix[x][y][dimension]
                id = " " if id is None else str(id)
                if id[0:2] == "S:":
                    id = id[2:3]
                print("{:<3}".format(id), end='')
                print(" | ", end='')
            print("")
        print("")