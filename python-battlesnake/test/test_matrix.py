import unittest
import json
import os, pathlib, sys

file_path = pathlib.Path(__file__).parent.resolve()
parent_path = os.path.join(file_path, "..")
sys.path.insert(1, parent_path)
from matrix import Matrix


class MatrixTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(parent_path, "fixtures/matrix_test.json")) as f:
            self.data = json.load(f)

    def test_creation(self):
        p = {"x": 1, "y": 2}
        m = Matrix(self.data["board"], p)
        # m.print()   # debugging
        # m.print(1)  # distance
        # m.print(2)  # space

        self.assertEqual(m.get_distance_to({"x": 3, "y": 4}), 4)
        self.assertEqual(m.get_distance_to({"x": 3, "y": 3}), 3)


if __name__ == "__main__":
    unittest.main()
