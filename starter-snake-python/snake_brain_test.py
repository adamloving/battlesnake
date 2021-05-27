import unittest

from snake_brain import SnakeBrain

class TestMoving(unittest.TestCase):

    def test_move(self):
        snake = SnakeBrain()
        self.assertEqual(snake.get_move({}), "left")

