import random

class SnakeBrain(object):

    def get_move(self, data):
      size = data["board"]["width"]
      head_position = data["you"]["head"]
      directions = ["up", "down", "left", "right"]
      random.shuffle(directions)
      valid_choices = []
      health = data["you"]["health"]

      for move in directions:
          position = self.get_next_position(head_position, move)
          if self.is_on_board(position, size) and self.is_open(position, data["board"]["snakes"]):
              valid_choices.append({
                "move": move,
                "position": position,
                "score": 1
              })

      # print(f"Valid choices: {len(valid_choices)} {valid_choices}")

      scored_choices = self.score_choices_based_on_food(data, valid_choices)
      # todo: score_based_on_next_head_positions(data["snakes"], valid_choices)
      # todo: score_choices_based_on_hazards

      # sort choices so best choice is first
      def by_score(choice):
        return choice["score"]
      scored_choices.sort(key=by_score)
      scored_choices.reverse()

      # print(f"sorted choices: {scored_choices}")
      best_choice = scored_choices[0]

      return best_choice["move"]

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
        choice["score"] = choice["score"] * self.get_food_score(
          health, choice["closest_food_distance"]
        )

      return choices

    # returns 1 if should go towards food, 0 if should ignore
    def get_food_score(self, health, distance):
        if health == 0: return 0 # avoid divide by 0
        if distance == 0: return 1 # avoid divide by 0

        # importance increases from 0 -> 1 as health decreases
        importance = (100 - health) ** 4 / (100 ** 4)

        # close = 1, far = 0
        proximity = 1 / distance

        # print(f"h={health} d={distance} i={importance} p={proximity} s={importance*proximity}")
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
