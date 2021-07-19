import unittest
import json

from board import Board

# to run in console me use: python snake_brain_test.py
class BoardTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/three_snakes.json') as f:
            self.data = json.load(f)

    # def test_creation(self):
    #     b = Board(self.data["board"])
    #     b.print()

    def test_generate(self):
        b = Board(self.data["board"])
        b.print()
        boards = b.generate()



if __name__ == '__main__':
    unittest.main()