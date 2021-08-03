import unittest
import json
import sys
import os
import pathlib

file_path = pathlib.Path(__file__).parent.resolve()
parent_path = os.path.join(file_path, "..")
sys.path.insert(1, parent_path)
from board import Board


class BoardTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(parent_path, "fixtures/example_turn.json")) as f:
            self.data = json.load(f)

    def test_generate(self):
        b = Board(self.data["board"], self.data["you"]["id"])
        # b.print()
        boards = b.generate()
        self.assertEqual(len(boards), 2)  # can go right or down
        # for board in boards:
        #     board.print()
        #     print(
        #         f"score me: {board.score_for_current_player()} others: {board.score_for_others()}"
        #     )


if __name__ == "__main__":
    unittest.main()
