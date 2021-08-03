import unittest
import json
import random

from snake_brain import SnakeBrain

# to run in console me use: python snake_brain_test.py
class SnakeBrainTest(unittest.TestCase):
    def setUp(self):
        with open("fixtures/example_turn.json") as f:
            self.data = json.load(f)

    def test_save_coefficients(self):
        snake = SnakeBrain(self.data)
        snake.save_coefficients()

    def test_get_hazard_score(self):
        self.data["board"]["snakes"][0]["health"] = 10
        self.data["you"]["health"] = 10
        self.data["board"]["hazards"].append({"x": 4, "y": 10})
        snake = SnakeBrain(self.data)
        snake.board.print()

        # far away, good health == 1
        self.assertAlmostEqual(snake.get_hazard_score(10, 100), 1, 1)

        # nearby, bad health = 0
        self.assertAlmostEqual(snake.get_hazard_score(0, 10), 0, 1)
        self.assertAlmostEqual(snake.get_hazard_score(0, 10), 0, 1)

        # nearby, good health - it's fine
        self.assertGreaterEqual(snake.get_hazard_score(1, 80), 0.9, 1)

    def test_hazard_scoring(self):
        self.data["board"]["snakes"][0]["health"] = 10
        self.data["you"]["health"] = 20

        for i in range(0, 11):
            self.data["board"]["hazards"].append({"x": i, "y": 10})  # top
            self.data["board"]["hazards"].append({"x": 0, "y": i})  # left

        snake = SnakeBrain(self.data)
        snake.board.print()
        snake.get_move()

    def test_space_scoring(self):
        snake = SnakeBrain(self.data)
        opponent = self.data["you"].copy()
        opponent["id"] = "opponent"
        opponent["head"] = {"x": 3, "y": 9}
        # opponent's body creates a tunnel that we don't want to go down
        opponent["body"] = [
            {"x": 3, "y": 9},
            {"x": 4, "y": 9},
            {"x": 5, "y": 9},
            {"x": 6, "y": 9},
            {"x": 6, "y": 10},
        ]
        self.data["board"]["snakes"].append(opponent)
        snake.board.print()

        snake.get_move()

        choices = snake.score_choices_based_on_space(
            self.data,
            [
                {"move": "right", "position": {"x": 3, "y": 10}},
                {"move": "down", "position": {"x": 2, "y": 9}},
            ],
        )
        print(f"{choices}")

    def test_hunt_scoring(self):
        snake = SnakeBrain(self.data)

        # full health? always hunt regardless of distance
        self.assertGreaterEqual(snake.get_hunting_score(100, 0), 0.95)
        self.assertLessEqual(snake.get_hunting_score(100, 3), 0.5)
        self.assertLessEqual(snake.get_hunting_score(100, 10), 0.1)

        # half health and close? hunt!
        self.assertGreaterEqual(snake.get_hunting_score(50, 0), 0.9)

        # half health and far away? probably not
        self.assertLessEqual(snake.get_hunting_score(50, 10), 0.5)

        # low health? don't hunt unless close
        self.assertLessEqual(snake.get_hunting_score(25, 10), 0.1)
        self.assertGreaterEqual(snake.get_hunting_score(25, 0), 0.7)

    def test_avoid_scoring(self):
        snake = SnakeBrain(self.data)
        self.assertGreaterEqual(
            snake.get_avoiding_score(4), 0.9
        )  # 4 away, okay to move there
        self.assertGreaterEqual(
            snake.get_avoiding_score(3), 0.8
        )  # 3 away neither here nor there
        self.assertLessEqual(snake.get_avoiding_score(2), 0.70)  # 2 away not so good
        self.assertLessEqual(snake.get_avoiding_score(1), 0.4)  # 1 away not good
        self.assertLessEqual(snake.get_avoiding_score(0), 0.1)  # 0 away don't do it

    def test_food_scoring(self):
        snake = SnakeBrain(self.data)
        snake.board.print()

        # If I'm healthy, food doesn't matter (score == 0)
        self.assertEqual(snake.get_food_score(100, 5, 100), 0)

        # If I'm starving, food is important (score == 1)
        self.assertGreaterEqual(snake.get_food_score(1, 1, 100), 0.95)

        # If I'm fine, and food is a little away from me, food is only a little important
        self.assertLessEqual(snake.get_food_score(40, 5, 100), 0.1)

        # I'm kindof hungry, and food sort of nearby, so important
        self.assertGreaterEqual(snake.get_food_score(20, 3, 100), 0.1)

        # I'm starving, and food sort of nearby, so very important
        self.assertGreaterEqual(snake.get_food_score(10, 3, 100), 0.20)

    # does it at least do something?
    def test_move(self):
        snake = SnakeBrain(self.data)
        move = snake.get_move()
        self.assertIn(move, ["left", "right", "up", "down"])

    # should stay on board no matter what size it is
    def xtest_stays_on_board(self):
        for size in range(7, 19):
            for x in range(0, size):
                for y in range(0, size):
                    self.data["board"]["height"] = size
                    self.data["board"]["width"] = size
                    head_position = {"x": x, "y": y}
                    self.data["you"]["head"] = head_position
                    self.data["you"]["body"] = [head_position]
                    self.data["you"]["length"] = 1
                    self.data["board"]["snakes"] = [self.data["you"]]
                    self.data["board"]["food"] = []

                    snake = SnakeBrain(self.data)
                    move = snake.get_move()

                    self.assertIn(move, ["left", "right", "up", "down"])

                    next_position = snake.get_next_position(head_position, move)

                    message = f"Board size {size}. Position {x},{y}. move = {move}"
                    self.assertGreaterEqual(next_position["x"], 0, message)
                    self.assertGreaterEqual(next_position["y"], 0, message)
                    self.assertLess(next_position["x"], size, message)
                    self.assertLess(next_position["y"], size, message)

    def test_avoids_self_collision(self):
        # a box where only way is is right
        self.data["you"]["body"] = [
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 0, "y": 2},
            {"x": 1, "y": 1},
            {"x": 1, "y": 0},
            {"x": 1, "y": 2},
            {"x": 2, "y": 0},
            {"x": 2, "y": 2},
        ]
        self.data["you"]["head"] = {"x": 1, "y": 1}
        self.data["board"]["snakes"][0] = self.data["you"]
        snake = SnakeBrain(self.data)
        move = snake.get_move()
        self.assertEqual(move, "right")

    def test_avoids_direct_collision(self):
        # head to head
        self.data["you"]["body"] = [
            {"x": 0, "y": 0},
        ]
        self.data["you"]["head"] = {"x": 0, "y": 0}
        self.data["board"]["snakes"][0] = self.data["you"]

        opponent = self.data["you"].copy()
        opponent["id"] = "opponent"
        opponent["head"] = {"x": 1, "y": 0}
        opponent["body"] = [{"x": 1, "y": 0}]

        self.data["board"]["snakes"].append(opponent)
        snake = SnakeBrain(self.data)
        snake.board.print()
        move = snake.get_move()
        self.assertEqual(move, "up")

    def test_avoids_potential_collision(self):
        # head to head
        self.data["you"]["body"] = [
            {"x": 0, "y": 0},
        ]
        self.data["you"]["head"] = {"x": 0, "y": 0}
        self.data["board"]["snakes"][0] = self.data["you"]

        opponent = self.data["you"].copy()
        opponent["id"] = "opponent"
        opponent["head"] = {"x": 2, "y": 0}
        opponent["body"] = [{"x": 2, "y": 0}, {"x": 3, "y": 0}]

        self.data["board"]["snakes"].append(opponent)

        snake = SnakeBrain(self.data)
        snake.board.print()
        move = snake.get_move()
        self.assertEqual(move, "up")

    def test_avoids_potential_collision_middle(self):
        # head to head
        self.data["you"]["body"] = [
            {"x": 3, "y": 3},
        ]
        self.data["you"]["head"] = {"x": 3, "y": 3}
        self.data["board"]["snakes"][0] = self.data["you"]

        opponent = self.data["you"].copy()
        opponent["id"] = "opponent"
        opponent["head"] = {"x": 4, "y": 3}
        opponent["body"] = [{"x": 4, "y": 3}]
        self.data["board"]["snakes"].append(opponent)

        snake = SnakeBrain(self.data)
        move = snake.get_move()
        self.assertIn(move, ["left", "up", "down"])

    def test_prints_board(self):
        self.data["board"]["snakes"].append(
            {
                "id": "A",
                "head": {"x": 7, "y": 5},
                "body": [{"x": 7, "y": 5}, {"x": 6, "y": 5}],
            }
        )
        self.data["board"]["hazards"].append({"x": 3, "y": 3})
        snake = SnakeBrain(self.data)
        snake.board.print()

    def test_seeks_food(self):
        snake = SnakeBrain(self.data)
        snake.board.print()
        self.data["you"]["health"] = 20
        move = snake.get_move()
        self.assertEqual(move, "down")


if __name__ == "__main__":
    unittest.main()
