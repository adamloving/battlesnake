import unittest
import json

from snake_brain import SnakeBrain

class TestMoving(unittest.TestCase):

    def setUp(self):
        with open('fixtures/example_turn.json') as f:
            self.data = json.load(f)

    def test_move(self):
        snake = SnakeBrain()
        self.assertIn(snake.get_move(self.data),
            ["left", "right", "up", "down"])

if __name__ == '__main__':
    unittest.main()