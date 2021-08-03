import os
import random
import cherrypy
import time

from snake_brain import SnakeBrain

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#888888",  # TODO: Personalize
            "head": "default",  # TODO: Personalize
            "tail": "default",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        # load last winner coefficients, mutate and save as current
        snake = SnakeBrain(data, "./files/last_winner.json")
        snake.mutate_coefficients()
        snake.save_coefficients() # save as files/current.json
        print("START")

        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        start_time = time.time()
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # print(cherrypy.request.json)

        # Choose a random direction to move in
        #possible_moves = ["up", "down", "left", "right"]
        #move = random.choice(possible_moves)

        snake = SnakeBrain(data)
        move = snake.get_move(data)


        print(f"Elapsed time: {time.time() - start_time}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        # presumably look and see if I'm on the board to determine if I won
        found = False
        me_id = data["you"]["id"]
        for snake in data["board"]["snakes"]:
            if snake["id"] == me_id:
                found = True

        if found:
            snake = SnakeBrain(data)
            snake.save_coefficients("./files/last_winner.json")
            snake.save_coefficients(f'./archive/generation-{snake.coefficients["generation"]}.json')
            print("END: alive!")

        print ("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
