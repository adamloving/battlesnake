import json
import random

class SnakeBrain(object):

    coefficients = {
      "generation": 1,
      "food": 1,
      "hunting": 1,
      "hazard": 1,
      "space": 1
    }

    def __init__(self, coefficient_file_name="./files/current.json"):
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

      # print(f"Valid choices: {len(valid_choices)} {valid_choices}")

      # (valid_choices and scored_choices are the same list)
      self.score_choices_based_on_food(data, valid_choices)
      self.score_choices_based_on_hunting(data, valid_choices)
      self.score_choices_based_on_optionality(data, valid_choices)
      self.score_choices_based_on_hazards(data, valid_choices)

      # average scores
      for choice in valid_choices:
        choice["score"] = sum([
          self.coefficients["food"] * choice["food_score"],
          self.coefficients["hunting"] * choice["hunting_score"],
          self.coefficients["hazard"] * choice["hazard_score"],
          self.coefficients["space"] * choice["optionality_score"],
        ]) / 4

      # sort choices so best choice is first
      def by_score(choice):
        return choice["score"]
      valid_choices.sort(key=by_score)
      valid_choices.reverse()

      print(f"----- At {head_position} -----")
      for i, choice in enumerate(valid_choices):
        print(f"{i}: {choice}")
      print("-------------------------------")

      # print(f"sorted choices: {scored_choices}")
      best_choice = valid_choices[0]

      return best_choice["move"]

    def get_hazard_score(self, distance):
        if distance == 0:
          return 0
        else:
          return 1

    def score_choices_based_on_hazards(self, data, valid_choices):
      for choice in valid_choices:
        choice["hazard_score"] = 1
        for hazard in data["board"]["hazards"]:
          distance = self.get_distance(choice["position"], hazard)
          choice["hazard_score"] = self.get_hazard_score(distance)

    def score_choices_based_on_food(self, data, choices):
      # todo: what happens when no food on board?
      health = data["you"]["health"]

      # for each choice, find closest_food_distance
      for choice in choices:
        choice["closest_food_distance"] = 9999999999
        for food in data["board"]["food"]:
          distance = self.get_distance(choice["position"], food)
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
              distance = self.get_distance(choice["position"], ophp)
              length = len(snake["body"])
              print(f"ophp: {ophp} {distance}")
              if distance < choice["closest_ophp_distance"]:
                print(f"found: {distance} {length}")
                choice["closest_ophp_distance"] = distance
                choice["closest_opponent_size"] = length

      print(f"{choices}")
      for choice in choices:
        print(f"get_hunting_score for {choice['position']} d={choice['closest_ophp_distance']}")
        if choice["closest_ophp_distance"] == 9999999999:
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

        # close = 1, far (10) = 0
        proximity = (-1 / 100) * (distance ** 2) + 1

        if length_delta > 0: # I'm longer
          # bugbug: not scaled to 1, skewed to hunt short snakes
          score = length_delta * importance * proximity # attack!
        else: # I'm same or shorter (avoid a little bit)
          if distance > 3:
            return 0.5
          else:
            score = 1 - (importance * proximity)

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

        # mark where the snakes are
        snake_number = 0
        for snake in data["board"]["snakes"]:
            for body_position in snake["body"]:
                matrix[body_position["x"]][body_position["y"]] = str(snake_number)
            snake_number += 1

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

    def score_choices_based_on_optionality(self, data, choices):
      size = data["board"]["width"]

      for choice in choices:
        open_count = 0
        position = choice["position"]
        for x in range(position["x"] - 3, position["x"] + 4):
          if x < 0 or x >= size: continue
          for y in range(position["y"] - 3, position["y"] + 4):
            if y < 0 or y >= size: continue
            space_position = { "x": x, "y": y}
            if self.is_open(space_position, data["board"]["snakes"]):
              if self.is_hazard(data, space_position):
                open_count += 0.5
              else:
                open_count += 1

        # print(f"open_count: {open_count}")
        choice["optionality_score"] = open_count / 49 # evaluating 7x7 grid

      return choices

    def is_hazard(self, data, position):
      for hazard in data["board"]["hazards"]:
        if position["x"] == hazard["x"] and position["y"] == hazard["y"]:
          return True
      return False
