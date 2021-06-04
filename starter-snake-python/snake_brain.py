import random
from collections import namedtuple

Point = namedtuple("Point", ("x", "y"))

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
        max_score = -9999999
        weighted_board = self.get_weighted_board(data)

        self.print_weighted_board(weighted_board)

        # which way can I go?
        for direction in directions:
            position = self.get_next_position(head_position, direction)
            if not self.is_on_board(board["width"], position):
                continue
            score = weighted_board[position["x"]][position["y"]]
            if score > max_score:
                max_score = score
                move = direction
                next_position = position

        # note: if there's no good moves, will default to last one considered
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
      board = self.get_weighted_board(data)
      return board[position["x"]][position["y"]] == 0.0 # todo - allow "maybe spots"

    # todo: distance to food, don't like corners
    def get_weighted_board(self, data):
      dimension = data["board"]["width"]
      board = [[0.5 for x in range(dimension)] for y in range(dimension)]

      # occupied spots
      for snake in data["board"]["snakes"]:
        # todo: how to account for fact that tail is leaving?
        for body_position in snake["body"]:
          board[body_position["x"]][body_position["y"]] = 0.0
          board = self.draw_overlay(board, body_position, 3, -0.1)

      # all potential occupied next head spots (except my own)
      for snake in data["board"]["snakes"]:
        if snake["id"] == data["you"]["id"]:
            continue
        head_position = snake["head"]
        for direction in ["up", "down", "left", "right"]:
          next_position = self.get_next_position(head_position, direction)
          if next_position["x"] >=0 and next_position["x"] < dimension and \
            next_position["y"] >= 0 and next_position["y"] < dimension:
            current_weight = board[next_position["x"]][next_position["y"]]
            board[next_position["x"]][next_position["y"]] = max(0, current_weight - 0.25)
            board = self.draw_overlay(board, next_position, 3, -0.1)

      # add points for food
      for food in data["board"]["food"]:
          # todo: increment scores around it too
          current_weight = board[food["x"]][food["y"]]
          if current_weight > 0:
              board[food["x"]][food["y"]] = min(1, current_weight + 0.1)
              board = self.draw_overlay(board, food, 3, 0.1)

      # print(f"board: {board}")
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

    def print_weighted_board(self, board):
        print("")
        max = len(board[0])
        for y in reversed(range(max)):
            print(" | ", end='')
            for x in range(max):
                # print(f"{x},{y}|", end='')
                print(str(board[x][y]).center(5), end='')
                print(" | ", end='')
            print("")
        print("")

    def print_board(self, data):
        size = data["board"]["width"]

        # initialize a list of lists
        matrix = [[" " for x in range(size)] for y in range(size)]

        print(f"{data['board']['snakes']}")

        # mark where the snakes are
        snake_number = 0
        for snake in data["board"]["snakes"]:
            for body_position in snake["body"]:
                matrix[body_position["x"]][body_position["y"]] = str(snake_number)
            snake_number += 1

        # todo: mark food and hazards

        # print it out
        print("")
        for y in reversed(range(size)):
            print(" | ", end='')
            for x in range(size):
                print(matrix[x][y].center(5), end='')
                print(" | ", end='')
            print("")
        print("")

        return matrix

    def draw_overlay(self, matrix, position, radius, delta):
        size = len(matrix[0])
        p = Point(*position.values())
        for x in range(p.x - radius, p.x + radius + 1):
            if x < 0 or x > size - 1: continue
            for y in range(p.y - radius, p.y + radius + 1):
                if y < 0 or y > size - 1: continue
                distance = abs(p.x - x) + abs(p.y - y)
                # todo decay with square of distance
                if distance == 0: d = delta
                else: d = (1/distance) * delta
                matrix[x][y] = round(matrix[x][y] + d, 2)
        return matrix

