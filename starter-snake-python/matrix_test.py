import unittest
import json

from matrix import Matrix

# to run in console me use: python snake_brain_test.py
class MatrixTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/matrix_test.json') as f:
            self.data = json.load(f)

    def test_creation(self):
        m = Matrix(self.data["board"], {"x": 0, "y": 2})
        m.print()
        m.print(1) # distance
        m.print(2) # space

    # def test_score_up(self):
    #     m = Matrix(self.data["board"])
    #     print(m.get_vector({"x": 0, "y": 3}))


if __name__ == '__main__':
    unittest.main()