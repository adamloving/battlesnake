import unittest
import json

from board import Board
from minimax import minimax

# to run in console me use: python snake_brain_test.py
class MinimaxTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/head_to_head_longer.json') as f:
            self.data = json.load(f)

    def test_minimax_longer(self):
        print("--- longer ---")
        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(minimax(b, 3))

    def test_minimax_shorter(self):
        print("--- shorter ---")
        with open('fixtures/head_to_head_shorter.json') as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(minimax(b, 1))

    def test_minimax_depth(self):
        print("*** depth 3 ***")
        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(minimax(b, 3))

    def test_minimax_sidebyside(self):
        print("--- side_by_side ---")
        with open('fixtures/side_by_side_shorter.json') as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(minimax(b, 2, True))

if __name__ == '__main__':
    unittest.main()