import unittest
import json

from board import Board

# to run in console me use: python snake_brain_test.py
class BoardTest(unittest.TestCase):

    def setUp(self):
        with open('fixtures/head_to_head_longer.json') as f:
            self.data = json.load(f)

    # def test_creation(self):
    #     b = Board(self.data["board"])
    #     b.print()

    def test_generate_longer(self):
        print("--- longer ---")
        with open('fixtures/head_to_head_longer.json') as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        boards = b.generate()
        for board in boards: 
            # print(f"{board.combo}")
            board.print() 
            print(f"score me: {board.score_for_current_player()} others: {board.score_for_others()}")

    def test_generate_shorter(self):
        print("--- shorter ---")
        with open('fixtures/head_to_head_shorter.json') as f:
            self.data = json.load(f)

        b = Board(self.data["board"], self.data["you"]["id"])
        b.print()
        boards = b.generate()
        for board in boards: 
            # print(f"{board.combo}")
            board.print() 
            print(f"score me: {board.score_for_current_player()} others: {board.score_for_others()}")


if __name__ == '__main__':
    unittest.main()