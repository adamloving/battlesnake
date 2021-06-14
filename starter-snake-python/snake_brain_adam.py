import random
from colr import color
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
        move = None
        next_position = None
        max_score = -9999999
        weighted_board = self.get_weighted_board(data)

        self.print_weighted_board(weighted_board)

        # which way can I go?
        for direction in directions:
            position = self.get_next_position(head_position, direction)
            if not self.is_on_board(board["width"], position):
                continue
            if move is None:
                move = direction
            score = weighted_board[position["x"]][position["y"]]
            print(f"At {head_position} Considering {direction} {score} ")
            if score > max_score:
                max_score = score
                move = direction

        # note: if there's no possible moves, returns None
        print("Move: " + move)
        return move

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
      size = data["board"]["width"]
      board = [[0.5 for x in range(size)] for y in range(size)]

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
          if next_position["x"] >=0 and next_position["x"] < size and \
            next_position["y"] >= 0 and next_position["y"] < size:
            current_weight = board[next_position["x"]][next_position["y"]]
            board[next_position["x"]][next_position["y"]] = max(0, current_weight - 0.25)
            board = self.draw_overlay(board, next_position, 3, -0.1)

      # add points for food (avoid if not hungry)
      # todo: make food more important if there is not much
      hungriness = (50 - data["you"]["health"]) / 100
      delta = (hungriness * 0.2)
      for food in data["board"]["food"]:
          # todo: increment scores around it too
          current_weight = board[food["x"]][food["y"]]
          if current_weight > 0:
              board[food["x"]][food["y"]] = max(0.1, min(0.9, current_weight + delta))
              board = self.draw_overlay(board, food, 5, delta)

      # avoid sides and corners (less room to move)
    #   for x in (0, size):
    #     for y in range(size):
    #         board = self.draw_overlay(board, { "x": x, "y": y }, 3, -0.05)
    #   for y in (0, size):
    #     for x in range(size):
    #         board = self.draw_overlay(board, { "x": x, "y": y }, 3, -0.05)

      # prefer the center
      self.draw_overlay(board, {
          "x": round(size/2),
          "y": round(size/2)
      }, size - 1, + 0.15)

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
        size = len(board[0])
        for y in reversed(range(size)):
            for x in range(size):
                value = max(0.0, round(board[x][y], 2))
                text = str(value).center(5)
                # for x in range(232, 255): print(color(str(x), fore=255, back=x))
                background_color = round(
                    232 + round(value * (255-232))
                )
                output = color(
                    text,
                    fore=255,
                    back=background_color
                )
                print(output, end='')
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

    # overlay can never result in 0
    def draw_overlay(self, matrix, position, radius, delta):
        size = len(matrix[0])
        p = Point(*position.values())
        for x in range(p.x - radius, p.x + radius + 1):
            if x < 0 or x > size - 1: continue
            if x == p.x: continue
            for y in range(p.y - radius, p.y + radius + 1):
                if y < 0 or y > size - 1: continue
                if y == p.y: continue
                if matrix[x][y] == 0: continue
                if matrix[x][y] == 1: continue
                distance = abs(p.x - x) + abs(p.y - y)
                # todo decay with square of distance
                if distance == 0: d = delta
                else: d = (1/distance) * delta
                new_value = round(matrix[x][y] + d, 2)
                matrix[x][y] = min(0.99, max(0.01, new_value))

        return matrix

