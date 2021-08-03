import json
import random

from board import Board
from matrix import Matrix


class SnakeBrain(object):

    coefficients = {
        "generation": 1,
        "food": 1,
        "hunting": 1,
        "hazard": 1,
        "space": 1,
        "avoiding": 1,
    }
    matrix_by_move = {}

    def __init__(self, data, coefficient_file_name="./files/current.json"):
        self.board = Board(data["board"])
        self.load_coefficients(coefficient_file_name)
        return

    def mutate_coefficients(self):
        self.coefficients["generation"] = self.coefficients["generation"] + 1
        for name in self.coefficients.keys():
            if name == "generation":
                continue
            self.coefficients[name] = self.coefficients[name] + (
                random.choice([-1, 1]) * 0.1
            )
        return

    def load_coefficients(self, name):
        with open(name, "r") as f:
            self.coefficients = json.load(f)
        return

    # after winning, save the mutated coefficients
    def save_coefficients(self, name="./files/current.json"):
        with open(name, "w") as f:
            json.dump(self.coefficients, f)
        return

    def get_move(self, data):
        head_position = data["you"]["head"]
        directions = ["up", "down", "left", "right"]
        random.shuffle(directions)
        valid_choices = []

        for move in directions:
            position = self.board.get_next_position(head_position, move)
            if self.board.is_on_board(position) and self.board.is_open(position):
                valid_choices.append({"move": move, "position": position, "score": 1})
                self.matrix_by_move[move] = Matrix(data["board"], position)

        print(f"Valid choices: {len(valid_choices)} {valid_choices}")

        # (valid_choices and scored_choices are the same list)
        self.score_choices_based_on_food(data, valid_choices)
        self.score_choices_based_on_hunting(data, valid_choices)
        self.score_choices_based_on_avoiding(data, valid_choices)
        self.score_choices_based_on_space(data, valid_choices)
        self.score_choices_based_on_hazards(data, valid_choices)

        # average scores
        for choice in valid_choices:
            choice["score"] = (
                sum(
                    [
                        self.coefficients["food"] * choice["food_score"],
                        self.coefficients["hunting"] * choice["hunting_score"],
                        self.coefficients["avoiding"] * choice["avoiding_score"],
                        self.coefficients["hazard"] * choice["hazard_score"],
                        self.coefficients["space"] * choice["space_score"],
                    ]
                )
                / 5
            )

        valid_choices = self.apply_filter_rules(data, valid_choices)

        # sort choices so best choice is first
        def by_score(choice):
            return choice["score"]

        valid_choices.sort(key=by_score)
        valid_choices.reverse()

        print(f"----- Turn {data['turn']} at {head_position} -----")
        for i, choice in enumerate(valid_choices):
            print(f"{i}: {self.choice_to_string(choice)}")
        print("-------------------------------")

        # print(f"sorted choices: {scored_choices}")
        if len(valid_choices) > 0:
            best_choice = valid_choices[0]
            return best_choice["move"]
        else:
            print("No valid moves")
            return None

    def apply_filter_rules(self, data, choices):
        good_choices = []

        for choice in choices:
            # bugbug: we might filter multiple bad choices here
            if (
                len(data["board"]["snakes"]) > 1
                and choice["closest_ophp_distance"] == 0
            ):
                continue
            good_choices.append(choice)

        # no good choices!
        if len(good_choices) == 0:
            good_choices = choices
        return good_choices

    # opposite of food score
    def get_hazard_score(self, distance, health):
        if health == 0:
            return 0  # avoid divide by 0
        if distance == 0:
            return 0  # avoid divide by 0

        # importance increases from 0 -> 1 as health decreases (reaches 1 at 30 health)
        importance = (100 - health + 30) ** 4 / (100 ** 4)
        importance = max(min(1, importance), 0)
        # https://www.desmos.com/calculator/ho1ztpfcp0

        # close (0) = 1, far (10) = 0
        proximity = 1 / ((distance + 1) ** 2)
        # https://www.desmos.com/calculator/yubw6ioyi8

        # bugbug: scale to 1 (normalize)
        print(
            f"hazard? h={health} d={distance} i={importance} p={proximity} s={1-(importance*proximity)}"
        )
        return 1 - (importance * proximity)

    def score_choices_based_on_hazards(self, data, valid_choices):
        for choice in valid_choices:
            distance = 99999
            choice["hazard_score"] = 1
            for hazard in data["board"]["hazards"]:
                # don't use the matrix, because our body might be in it
                distance = min(distance, self.board.get_distance(choice["position"], hazard))
                # print(f"{choice['position']} {self.get_distance(choice['position'], hazard)} {hazard}")

            # calc based on nearest hazard
            choice["hazard_score"] = self.get_hazard_score(
                distance, data["you"]["health"]
            )

            # HACK: in hazard, further from edge is better
            if choice["hazard_score"] == 0:
                print("Hazard hack")
                size = data["board"]["width"]
                p = choice["position"]
                # interior scores higher than edges
                choice["hazard_score"] = 0.1 * min(
                    p["x"], size - p["x"], p["y"], size - p["y"]
                )

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

        # for all choices, find the one closest to food
        closest_food_distance = 99999999999
        for choice in choices:
            if choice["closest_food_distance"] < closest_food_distance:
                closest_food_distance = choice["closest_food_distance"]

        # based on how hungry we are, increment score for choice based to food
        for choice in choices:
            choice["food_score"] = self.get_food_score(
                health, choice["closest_food_distance"], data["turn"]
            )

        return choices

    def score_choices_based_on_hunting(self, data, choices):
        my_id = data["you"]["id"]
        my_length = len(data["you"]["body"])
        health = data["you"]["health"]
        size = data["board"]["width"]

        for choice in choices:
            # find nearest prey_possible_head_position for smaller snakes
            choice["closest_pphp_distance"] = 9999999999
            choice["closest_prey_size"] = 9999999999
            for snake in data["board"]["snakes"]:
                if snake["id"] == my_id:
                    continue
                if snake["length"] >= my_length:
                    continue
                prey_head_position = snake["head"]
                for direction in ["up", "down", "left", "right"]:
                    pphp = self.board.get_next_position(prey_head_position, direction)
                    if self.board.is_on_board(pphp) and self.board.is_open(
                        pphp
                    ):
                        distance = self.matrix_by_move[choice["move"]].get_distance_to(
                            pphp
                        )
                        # print(f"pphp: {pphp} {distance}")
                        if distance < choice["closest_pphp_distance"]:
                            # print(f"nearest prey: d={distance} l={snake['length']}")
                            choice["closest_pphp_distance"] = distance

        for choice in choices:
            if choice["closest_pphp_distance"] >= 10:
                choice["hunting_score"] = 0
            else:
                choice["hunting_score"] = self.get_hunting_score(
                    health, choice["closest_pphp_distance"]
                )
            # print(f"get_hunting_score for {choice['position']} d={choice['closest_pphp_distance']} s={round(choice['hunting_score'], 5)}")

        return choices

    def score_choices_based_on_avoiding(self, data, choices):
        my_id = data["you"]["id"]
        my_length = data["you"]["length"]
        size = data["board"]["width"]

        for choice in choices:
            # find nearest opponent_possible_head_position for smaller snakes
            choice["closest_ophp_distance"] = 9999999999
            choice["closest_opponent_size"] = 9999999999
            for snake in data["board"]["snakes"]:
                if snake["id"] == my_id:
                    continue
                if snake["length"] < my_length:
                    continue
                opponent_head_position = snake["head"]
                for direction in ["up", "down", "left", "right"]:
                    ophp = self.board.get_next_position(
                        opponent_head_position, direction
                    )
                    if self.board.is_on_board(ophp) and self.board.is_open(ophp):
                        distance = self.matrix_by_move[choice["move"]].get_distance_to(
                            ophp
                        )
                        # if distanceprint(f"ophp: {ophp} {distance}")
                        if distance < choice["closest_ophp_distance"]:
                            # print(f"nearest opponent: d={distance} l={snake['length']}")
                            choice["closest_ophp_distance"] = distance

        for choice in choices:
            if choice["closest_ophp_distance"] >= 10:
                choice["avoiding_score"] = 1
            else:
                choice["avoiding_score"] = self.get_avoiding_score(
                    choice["closest_ophp_distance"]
                )
            # print(f"get_avoiding_score for {choice['position']} d={choice['closest_ophp_distance']} s={round(choice['avoiding_score'], 5)}")

        return choices

    # distance input should be distance to nearest _potential_ next head
    def get_hunting_score(self, health, distance):
        # full health = 1 -> 0 no health, no hunt
        importance = 1 - (2.72 ** (-health / 20))

        # close (0) = 1 good, far (5) = 0 bad
        distance = min(5, distance)  # max 5 distance for formula
        proximity = (5 - distance) ** 2 / (5 ** 2)
        # https://www.desmos.com/calculator/ho1ztpfcp0

        score = importance * proximity  # attack!

        print(f"hunt? h={health} d={distance} i={importance} p={proximity} s={score}")
        return score

    def get_avoiding_score(self, distance):
        distance = min(4, distance)  # max 5 distance for formula

        proximity = (4 - distance) ** 1.5 / (4 ** 1.5)
        # https://www.desmos.com/calculator/ho1ztpfcp0

        # close (1) = 0 bad, far (4) = 1 good
        score = 1 - proximity

        print(f"avoid? d={distance} p={proximity} s={score}")
        return score

    # returns 1 if should go towards food, 0 if should ignore
    def get_food_score(self, health, distance, turn):
        if health == 0:
            return 0  # avoid divide by 0
        if distance == 0:
            return 1  # avoid divide by 0

        # each turn costs 1 health. to aggressively go after food for first 50 turns,
        # use turn as health (start hungry, and back off)
        if turn <= 50:
            health = turn

        # importance increases from 0 -> 1 as health decreases
        importance = (100 - health) ** 4 / (100 ** 4)

        # close = 1, far = 0
        proximity = 1 / distance  # should

        print(
            f"eat? t={turn} h={health} d={distance} i={importance} p={proximity} s={round(importance*proximity, 5)}"
        )
        return importance * proximity

    def score_choices_based_on_space(self, data, choices):
        for choice in choices:
            choice["space_score"] = self.matrix_by_move[choice["move"]].get_space_score(
                choice["position"]
            )

        return choices

    def choice_to_string(self, c):
        return (
            f"m:{c['move']} {c['position']['x']},{c['position']['y']} "
            + f"s:{round(c['score'], 5)} "
            + f"food: {round(c['food_score'], 5)} "
            + f"hunting: {round(c['hunting_score'], 5)} "
            + f"avoiding: {round(c['avoiding_score'], 5)} "
            + f"space: {round(c['space_score'], 5)} "
            + f"hazard: {round(c['hazard_score'], 5)}"
        )
