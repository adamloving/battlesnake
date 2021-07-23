import unittest
import json

from matrix import Matrix

# to run in console me use: python snake_brain_test.py
class MatrixTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/matrix_test.json') as f:
            self.data = json.load(f)

    def test_creation(self):
        p = {"x": 1, "y": 2}
        m = Matrix(self.data["board"], p)
        m.print()  # debugging
        m.print(1) # distance
        m.print(2) # space

        self.assertEqual(m.get_distance_to({"x": 3, "y": 4}), 4)
        self.assertEqual(m.get_distance_to({"x": 3, "y": 3}), 3)



    # def test_score_up(self):
    #     m = Matrix(self.data["board"])
    #     print(m.get_vector({"x": 0, "y": 3}))


if __name__ == '__main__':
    unittest.main()