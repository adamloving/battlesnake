import json
import random

from matrix import Matrix

class SnakeBrain(object):

    coefficients = {
      "generation": 1,
      "food": 1,
      "hunting": 1,
      "hazard": 1,
      "space": 1,
    }
    matrix_by_move = {}

    def __init__(self, data, coefficient_file_name="./files/current.json"):
      self.load_coefficients(coefficient_file_name)
      # print(f"Loaded: {self.coefficients}")
      return

    def mutate_coefficients(self):
      self.coefficients["generation"] = self.coefficients["generation"] + 1
      for name in self.coefficients.keys():
        if name == "generation": continue
        self.coefficients[name] = self.coefficients[name] + (random.choice([-1, 1]) * 0.1)
      return

    def load_coefficients(self, name):
      with open(name, 'r') as f:
        self.coefficients = json.load(f)
      return

    # only save after win
    def save_coefficients(self, name="./files/current.json"):
      with open(name, 'w') as f:
        json.dump(self.coefficients, f)
      return

    def get_move(self, data):
      size = data["board"]["width"]
      head_position = data["you"]["head"]
      directions = ["up", "down", "left", "right"]
      random.shuffle(directions)
      valid_choices = []

      for move in directions:
          position = self.get_next_position(head_position, move)
          if self.is_on_board(position, size) and self.is_open(position, data["board"]["snakes"]):
              valid_choices.append({
                "move": move,
                "position": position,
                "score": 1
              })
              self.matrix_by_move[move] = Matrix(data["board"], position)

      print(f"Valid choices: {len(valid_choices)} {valid_choices}")

      # (valid_choices and scored_choices are the same list)
      self.score_choices_based_on_food(data, valid_choices)
      self.score_choices_based_on_hunting(data, valid_choices)
      self.score_choices_based_on_space(data, valid_choices)
      self.score_choices_based_on_hazards(data, valid_choices)

      # average scores
      for choice in valid_choices:
        choice["score"] = sum([
          self.coefficients["food"] * choice["food_score"],
          self.coefficients["hunting"] * choice["hunting_score"],
          self.coefficients["hazard"] * choice["hazard_score"],
          self.coefficients["space"] * choice["space_score"],
        ]) / 4

      # sort choices so best choice is first
      def by_score(choice):
        return choice["score"]
      valid_choices.sort(key=by_score)
      valid_choices.reverse()

      print(f"----- Turn {data['turn']} at {head_position} -----")
      for i, choice in enumerate(valid_choices):
        print(f"{i}: {choice}")
      print("-------------------------------")

      # print(f"sorted choices: {scored_choices}")
      if len(valid_choices) > 0:
        best_choice = valid_choices[0]
        return best_choice["move"]
      else:
        print("No valid moves")
        return None

    # opposite of food score
    def get_hazard_score(self, distance, health):
        if health == 0: return 0 # avoid divide by 0
        if distance == 0: return 0 # avoid divide by 0

        # importance increases from 0 -> 1 as health decreases (reaches 1 at 30 health)
        importance = (100 - health + 30) ** 4 / (100 ** 4)
        importance = max(min(1, importance), 0)
        # https://www.desmos.com/calculator/ho1ztpfcp0

        # close = 1, far (10) = 0
        proximity = 1 / (distance ** 0.6)
        # https://www.desmos.com/calculator/yubw6ioyi8

        # bugbug: scale to 1 (normalize)
        print(f"hazard? h={health} d={distance} i={importance} p={proximity} s={1-(importance*proximity)}")
        return 1 - (importance * proximity)

    def score_choices_based_on_hazards(self, data, valid_choices):
      for choice in valid_choices:
        matrix = self.matrix_by_move[choice["move"]]
        distance = 99999
        choice["hazard_score"] = 1
        for hazard in data["board"]["hazards"]:
          distance = min(distance,
            matrix.get_distance_to(hazard)
          )

        # calc based on nearest hazard
        choice["hazard_score"] = self.get_hazard_score(distance, data["you"]["health"])

    def score_choices_based_on_food(self, data, choices):
      # todo: what happens when no food on board?
      health = data["you"]["health"]

      # for each choice, find closest_food_distance
      for choice in choices:
        choice["closest_food_distance"] = 9999999999
        for food in data["board"]["food"]:
          distance = self.matrix_by_move[choice["move"]].get_distance_to(food)
          if distance < choice["closest_food_distance"]:
            choice["closest_food_distance"] = distance

      # for all choices, find the one closes to food
      closest_food_distance = 99999999999
      for choice in choices:
        if choice["closest_food_distance"] < closest_food_distance:
          closest_food_distance = choice["closest_food_distance"]

      # based on how hungry we are, increment score for choice based to food
      for choice in choices:
        choice["food_score"] = self.get_food_score(health, choice["closest_food_distance"])

      return choices

    def score_choices_based_on_hunting(self, data, choices):
      my_id = data["you"]["id"]
      my_length = len(data["you"]["body"])
      health = data["you"]["health"]
      size = data["board"]["width"]

      for choice in choices:
        # opponent_possible_head_position
        choice["closest_ophp_distance"] = 9999999999
        choice["closest_opponent_size"] = 9999999999
        for snake in data["board"]["snakes"]:
          if snake["id"] == my_id:
            continue
          opponent_head_position = snake["head"]
          for direction in ["up", "down", "left", "right"]:
            ophp = self.get_next_position(opponent_head_position, direction)
            if self.is_on_board(ophp, size) and \
              self.is_open(ophp, data["board"]["snakes"]):
              distance = self.matrix_by_move[choice["move"]].get_distance_to(ophp)
              length = len(snake["body"])
              # if distanceprint(f"ophp: {ophp} {distance}")
              if distance < choice["closest_ophp_distance"]:
                print(f"nearest opponent: d={distance} l={length}")
                choice["closest_ophp_distance"] = distance
                choice["closest_opponent_size"] = length

      for choice in choices:
        print(f"get_hunting_score for {choice['position']} d={choice['closest_ophp_distance']}")
        if choice["closest_ophp_distance"] >= 10:
          choice["hunting_score"] = 0
        else:
          choice["hunting_score"] = self.get_hunting_score(
            health,
            choice["closest_ophp_distance"],
            my_length - choice["closest_opponent_size"]
          )

      return choices

    # distance input should be distance to nearest _potential_ next head
    # (otherwise use score = 1)
    def get_hunting_score(self, health, distance, length_delta):
        # full health = 1 -> 0 no health, no hunt
        importance = 1 - (2.72 ** (- health / 20))

        distance = min(5, distance) # max 5 distance for formula

        # close = 1, far (5) = 0
        proximity = (5 - distance + 1) ** 2 / (5 ** 2)
        # https://www.desmos.com/calculator/ho1ztpfcp0

        if length_delta > 0: # I'm longer
          score = importance * proximity # attack!
        else: # I'm same or shorter (avoid)
          score = 1 - proximity

        print(f"hunt? h={health} d={distance} ld={length_delta} i={importance} p={proximity} s={score}")
        return score

    # returns 1 if should go towards food, 0 if should ignore
    def get_food_score(self, health, distance):
        if health == 0: return 0 # avoid divide by 0
        if distance == 0: return 1 # avoid divide by 0

        # importance increases from 0 -> 1 as health decreases
        importance = (100 - health) ** 4 / (100 ** 4)

        # close = 1, far = 0
        proximity = 1 / distance

        print(f"eat? h={health} d={distance} i={importance} p={proximity} s={round(importance*proximity, 10)}")
        return importance * proximity

    def get_distance(self, p1, p2):
      dist_x = abs(p1["x"] - p2["x"])
      dist_y = abs(p1["y"] - p2["y"])
      return dist_x + dist_y

    def is_on_board(self, position, size):
      if position["x"] < 0:
        return False
      if position["y"] < 0:
        return False
      if position["x"] > size - 1:
        return False
      if position["y"] > size - 1:
        return False

      return True

    def is_open(self, position, snakes):
      for snake in snakes:
        for body_position in snake["body"]:
          if body_position["x"] == position["x"] and body_position["y"] == position["y"]:
            return False

      return True

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

    def print_board(self, data):
        size = data["board"]["width"]

        # initialize a list of lists
        matrix = [[" " for x in range(size)] for y in range(size)]

        # This should mark the food in the board
        # This passes the checker, but I don't know how to get print the board so I can see if it actually works
        snake_number = "F"
        for food in data["board"]["food"]:
          for food_position in data["board"]["food"]:
            matrix[food_position["x"]][food_position["y"]] = str(snake_number)

        # This should mark the hazards in the board
        # This passes the checker, but I don't know how to get print the board so I can see if it actually works
        snake_number = "H"
        for hazard in data["board"]["hazards"]:
          for hazard_position in data["board"]["hazards"]:
            matrix[hazard_position["x"]][hazard_position["y"]] = str(snake_number)

        # mark where the snakes are
        snake_number = 0
        for snake in data["board"]["snakes"]:
            for body_position in snake["body"]:
                matrix[body_position["x"]][body_position["y"]] = str(snake_number)
            snake_number += 1

        # print it out
        print("")
        for y in reversed(range(size)):
            print(" | ", end='')
            for x in range(size):
                print(f"{matrix[x][y]}", end='')
                print(" | ", end='')
            print("")
        print("")

        return matrix

    def score_choices_based_on_space(self, data, choices):
      for choice in choices:
        choice["space_score"] = \
          self.matrix_by_move[choice["move"]].get_space_score(choice["position"])

      return choices

    def is_hazard(self, data, position):
      return position in data["board"]["hazards"]

