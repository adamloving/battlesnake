import unittest
import json, os, sys, pathlib

file_path = pathlib.Path(__file__).parent.resolve()
parent_path = os.path.join(file_path, "..")
sys.path.insert(1, parent_path)
from board import Board
from maximax import maximax

class MaximaxTest(unittest.TestCase):
    def setUp(self):
        with open(
            os.path.join(parent_path, "fixtures/scenarios/up_when_facing_longer.json")
        ) as f:
            self.data = json.load(f)

    def xtest_maximax_longer(self):
        # print("--- longer ---")
        b = Board(self.data["board"], self.data["you"]["id"])
        # b.print()
        maximax(b, 1)

    def xtest_maximax_shorter(self):
        # print("--- shorter ---")
        with open(
            os.path.join(
                parent_path, "fixtures/scenarios/down_side_by_side_shorter.json"
            )
        ) as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        # b.print()
        maximax(b, 1)

    def xtest_maximax_depth(self):
        # print("*** depth 3 ***")
        b = Board(self.data["board"], self.data["you"]["id"])
        # b.print()
        maximax(b, 3)

    def test_maximax_sidebyside(self):
        # print("--- side_by_side ---")
        with open(
            os.path.join(
                parent_path, "fixtures/scenarios/down_side_by_side_shorter.json"
            )
        ) as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        # b.print()
        maximax(b, 3)


if __name__ == "__main__":
    unittest.main()
