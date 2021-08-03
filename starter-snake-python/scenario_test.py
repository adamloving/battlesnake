import argparse
import logging
import unittest
import json
import random
import os

DIRECTIONS = ["up", "down", "left", "right"]

from snake_brain import SnakeBrain

# to run in console use: python scenario_test.py
# to run one sceenario with debugging: python scenario_test.py --test=right_when_shortest --log=debug
def test_scenarios(selected_test_name="all"):
    path = os.path.join(os.getcwd(), "fixtures/scenarios")
    for file_name in os.listdir(path):
        test_name = file_name.split(".")[0]
        if selected_test_name != "all" and test_name != selected_test_name:
            continue
        expected_move = file_name.split("_")[0]
        with open(os.path.join(path, file_name), "r") as f:
            data = json.load(f)
            # todo validate that file is consistent (snakes[0] === you) because may be hand coded
            # also validate that lengths are correct
            snake = SnakeBrain(data)
            move = snake.get_move()

            if expected_move in DIRECTIONS:
                if move == expected_move:
                    print(f"---- PASS {test_name} ----")
                else:
                    print(f"---- FAIL {test_name} ----")
                    snake.board.print()
                    snake.print_choices()
                    print(f"Failed: {test_name} expected {expected_move} got {move}")
                    print("")
            else:
                print(f"---- NO EXPECTATION {test_name} ----")
                # snake.board.print()
                print("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        default="",
        help="Run one test. Example --test right_when_shortest, default=all",
    )
    parser.add_argument(
        "--log",
        default="warning",
        help="Provide logging level. Example --log debug, default=warning",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.log.upper())
    logging.info("Logging now setup.")

    test_scenarios(args.test)
