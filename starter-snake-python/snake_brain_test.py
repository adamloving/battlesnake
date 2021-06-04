import unittest
import json
import random

from snake_brain import SnakeBrain

class SnakeBrainTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/example_turn.json') as f:
            self.data = json.load(f)

    # does it at least do something?
    def test_move(self):
        snake = SnakeBrain()
        move = snake.get_move(self.data)
        self.assertIn(move, ["left", "right", "up", "down"])

    # should stay on board (or return None) no matter what the size of it
    def test_stays_on_board(self):
        for size in range(7, 19):
          for x in range(0, size):
            for y in range(0, size):
              self.data["board"]["height"] = size
              self.data["board"]["width"] = size
              head_position = {"x": x, "y": y }
              self.data["you"]["head"] = head_position
              self.data["you"]["body"] = [head_position]
              self.data["you"]["length"] = 1
              self.data["board"]["snakes"] = [ self.data["you"] ]
              self.data["board"]["food"] = []

              snake = SnakeBrain()
              move = snake.get_move(self.data)

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
        snake = SnakeBrain()
        move = snake.get_move(self.data)
        self.assertEqual(move, "right")

    def xtest_get_weighted_board(self):
        snake = SnakeBrain()
        spots = snake.get_weighted_board(self.data)
        # open
        self.assertEqual(0.5, spots[0][0])
        # my body
        self.assertEqual(0.0, spots[1][9])
        # food
        self.assertEqual(0.6, spots[0][8])

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

    # python snake_brain_test.py SnakeBrainTest.test_prints_board
    def test_prints_weighted_board(self):
        snake = SnakeBrain()
        board = snake.get_weighted_board(self.data)
        snake.print_weighted_board(board)

    def test_prints_board(self):
        self.data["board"]["snakes"].append({
            "head": { "x": 7, "y": 5 },
            "body": [{ "x": 7, "y": 5 }, {"x": 6, "y": 5 }]
        })
        self.data["board"]["hazards"].append({
            "x": 3, "y": 3
        })
        snake = SnakeBrain()
        matrix = snake.print_board(self.data)

        self.assertEqual(matrix[7][5], "1")
        # self.assertEqual(matrix[0][8], "F")
        # self.assertEqual(matrix[5][5], "F")
        # self.assertEqual(matrix[3][3], "H")

    def test_draw_overlay(self):
        snake = SnakeBrain()
        matrix = [[0.5 for x in range(10)] for y in range(10)]
        matrix = snake.draw_overlay(matrix, {"x": 5, "y": 5 }, 3, 0.1)
        snake.print_weighted_board(matrix)

if __name__ == '__main__':
    unittest.main()