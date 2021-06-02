import unittest
import json
import random

from snake_brain import SnakeBrain

class SnakeBrainTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/example_turn.json') as f:
            self.data = json.load(f)

    # does it at least do something?
    def xtest_move(self):
        snake = SnakeBrain()
        move = snake.get_move(self.data)
        self.assertIn(move, ["left", "right", "up", "down"])

    # should stay on board (or return None) no matter what the size of it
    def xtest_stays_on_board(self):
        dimension = random.randrange(5, 100) # random square board size
        self.data["board"]["height"] = dimension
        self.data["board"]["width"] = dimension

        snake = SnakeBrain()
        move = snake.get_move(self.data)

        head_position = {
            "x": self.data["you"]["head"]["x"],
            "y": self.data["you"]["head"]["y"]
        }
        next_position = snake.get_next_position(head_position, move)

        if next_position is None:
            print("need more specific test")
        else:
            self.assertGreaterEqual(next_position["x"], 0)
            self.assertGreaterEqual(next_position["y"], 0)
            self.assertLess(next_position["x"], dimension)
            self.assertLess(next_position["y"], dimension)

    def xtest_avoids_self_collision(self):
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
        snake = SnakeBrain()
        move = snake.get_move(self.data)
        self.assertEqual(move, "right")

    def xtest_get_uncontested_spots(self):
        snake = SnakeBrain()
        spots = snake.get_uncontested_spots(self.data)
        self.assertEqual(0.0, spots[1][9])
        self.assertEqual(0.0, spots[1][10])

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
        snake = SnakeBrain()
        move = snake.get_move(self.data)
        self.assertEqual(move, "up")

    def xtest_avoids_potential_collision(self):
        # head to head
        self.data["you"]["body"] = [
            {"x": 0, "y": 0},
        ]
        self.data["you"]["head"] = {"x": 0, "y": 0}
        self.data["board"]["snakes"][0] = self.data["you"]

        opponent = self.data["you"].copy()
        opponent["id"] = "opponent"
        opponent["head"] = {"x": 2, "y": 0}
        opponent["body"] = [{"x": 2, "y": 0}]

        self.data["board"]["snakes"].append(opponent)
        snake = SnakeBrain()
        move = snake.get_move(self.data)
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
        snake = SnakeBrain()
        move = snake.get_move(self.data)
        self.assertIn(move, ["left", "up", "down"])



if __name__ == '__main__':
    unittest.main()