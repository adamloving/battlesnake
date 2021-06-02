import random

class SnakeBrain(object):

    # returns None if no valid move
    def get_move(self, data):
        board = data["board"]
        head_position = {
            "x": data["you"]["head"]["x"],
            "y": data["you"]["head"]["y"]
        }
        directions = ["up", "down", "left", "right"]
        random.shuffle(directions)
        move = directions[0] # random default move
        next_position = self.get_next_position(head_position, move)

        center = {
            "x": round(board["width"] / 2),
            "y": round(board["height"] / 2)
        }
        min_dist_to_center = 9999999

        # which way can I go?
        for direction in directions:
            position = self.get_next_position(head_position, direction)
            dist_to_center = self.get_distance(center, position)
            if self.is_on_board(board["width"], position) and \
                self.is_uncontested(data, position) and \
                dist_to_center < min_dist_to_center:
                min_dist_to_center = dist_to_center
                move = direction
                next_position = position

        if self.is_on_board(board["width"], next_position):
            print("Move: " + move)
            return move
        else:
            print("Move: None")
            return None

    def is_on_board(self, size, position):
        return position["x"] >= 0 and \
            position["x"] < size and \
            position["y"] >= 0 and \
            position["y"] < size

    def is_collision_with_snakes(self, data, position):
      for snake in data["board"]["snakes"]:
        for body_position in snake["body"]:
            if position["x"] == body_position["x"] and \
                position["y"] == body_position["y"]:
                return True
      return False

    def is_uncontested(self, data, position):
      board = self.get_uncontested_spots(data)
      return board[position["x"]][position["y"]] > 0.5 # todo - allow "maybe spots"

    # need to consider where others might move
    def get_uncontested_spots(self, data):
      dimension = data["board"]["width"]
      board = [[1.0 for x in range(dimension)] for y in range(dimension)]

      # occupied spots
      for snake in data["board"]["snakes"]:
        for body_position in snake["body"]:
          board[body_position["x"]][body_position["y"]] = 0.0

      # all potential occupied next head spots (except my own)
      for snake in data["board"]["snakes"]:
        if snake["id"] == data["you"]["id"]:
            continue
        head_position = snake["head"]
        for direction in ["up", "down", "left", "right"]:
          next_position = self.get_next_position(head_position, direction)
          if next_position["x"] >=0 and next_position["x"] < dimension and \
            next_position["y"] >= 0 and next_position["y"] < dimension:
            board[next_position["x"]][next_position["y"]] = \
                board[next_position["x"]][next_position["y"]] - 0.5

      print(f"uncontested {board}")
      return board

    # note: no bounds check
    def get_next_position(self, current_position, direction):
        new_position = current_position.copy()
        if direction == "up":
            new_position["y"] = new_position["y"] + 1
        elif direction == "down":
            new_position["y"] = new_position["y"] - 1
        elif direction == "right":
            new_position["x"] = new_position["x"] + 1
        elif direction == "left":
            new_position["x"] = new_position["x"] - 1

        return new_position

    def get_distance(self, a, b):
        return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
