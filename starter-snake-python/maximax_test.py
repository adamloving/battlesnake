import unittest
import json

from board import Board
from maximax import maximax

# to run in console me use: python snake_brain_test.py
class MaximaxTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/short_snake.json') as f:
            self.data = json.load(f)

    def xtest_maximax_depth0(self):
        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(maximax(b, 0))

    def test_maximax_depth(self):
        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(maximax(b, 3))

if __name__ == '__main__':
    unittest.main()