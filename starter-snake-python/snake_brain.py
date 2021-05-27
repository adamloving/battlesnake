import random

class SnakeBrain(object):

    def get_move(self, data):
        board = data["board"]
        head_position = {
            "x": data["you"]["head"]["x"],
            "y": data["you"]["head"]["y"]
        }
        directions = ["up", "down", "left", "right"]
        random.shuffle(directions)

        center = {
            "x": round(board["width"] / 2),
            "y": round(board["height"] / 2)
        }
        min_dist_to_center = 9999999
        move = None

        # which way can I go?
        for direction in directions:
            position = self.get_next_position(head_position, direction)
            dist_to_center = self.get_distance(center, position)
            if self.is_on_board(board["width"], position) and \
                not self.is_self_collision(data, position) and \
                dist_to_center < min_dist_to_center:
                min_dist_to_center = dist_to_center
                move = direction

        print("Move: " + direction)
        return move

    def is_on_board(self, size, position):
        return position["x"] >= 0 and \
            position["x"] < size and \
            position["y"] >= 0 and \
            position["y"] < size

    def is_self_collision(self, data, position):
        body = data["you"]["body"]
        for body_position in body:
            if position["x"] == body_position["x"] and \
                position["y"] == body_position["y"]:
                return True

        return False

    def get_next_position(self, current_position, direction):
        new_position = current_position.copy()
        if direction == "up":
            new_position["y"] = new_position["y"] + 1
        elif direction == "down":
            new_position["y"] = new_position["y"] - 1
        elif direction == "right":
            new_position["x"] = new_position["x"] + 1
        elif direction == "left":
            new_position["x"] = new_position["x"] - 1

        return new_position

    # distance in moves
    def get_distance(self, a, b):
        return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])

