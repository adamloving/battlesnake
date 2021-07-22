import unittest
import json

from board import Board
from maximax import maximax

# to run in console me use: python snake_brain_test.py
class MaximaxTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/head_to_head_longer.json') as f:
            self.data = json.load(f)

    def test_maximax_longer(self):
        print("--- longer ---")
        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(maximax(b, 1))

    def test_maximax_shorter(self):
        print("--- shorter ---")
        with open('fixtures/head_to_head_shorter.json') as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(maximax(b, 1))

    def test_maximax_depth(self):
        print("*** depth 3 ***")
        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        print(maximax(b, 3))

if __name__ == '__main__':
    unittest.main()