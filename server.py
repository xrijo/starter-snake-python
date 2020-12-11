import os
import random

import cherrypy
import copy
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
            "color": "#006622",  # TODO: Personalize
            "head": "tongue",  # TODO: Personalize
            "tail": "sharp",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json
        max_depth = 2
        move, est_steps = self.eval_deep_state(data, max_depth,'first')
        if est_steps < max_depth:
          print('I WILL CRASH SOON :/   AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHH')
        print ('Moving ', move)
        return {"move": move, "shout": ''}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"

    def eval_deep_state(self, data, depth, last_move):
      # This function returns wether it is possible to perform a move 
      # that won´t kill the snake within x moves
      possible_moves = ["up", "down", "left", "right"]
      if last_move in possible_moves:
        possible_moves.remove(self.opposite(last_move))

      # checkout what happens if you don´t shuffle it
      random.shuffle(possible_moves)

      best_move, steps = "up", -1
      for move in possible_moves:
        if self.is_legal(move,data):
          if depth == 0:
            possible = 1
          else:
            est_data = self.next_estimated_data(data, move)
            possible = 1 + self.eval_deep_state(est_data, depth-1, move)[1]
          if possible == depth + 1:
            #result found
            return move, True
          elif possible > steps:
            best_move = move
            steps = possible
      return best_move, steps

    def opposite(self, move):
      if move == "up":
        result = "down"
      elif move == "down":
        result = "up"
      elif move == "left":
        result = "right"
      else:
        result = "left"
      return result

    def is_legal(self, move, data):
        # This function evaluates the legitemacy of the chosen move

        # Extract own position
        pos_prev = data['you']['body'][1]
        pos_next = self.next_position(data, move)


        # prevent running into snakes
        snakes = data['board']['snakes']
        for snake in snakes:
          if pos_next in snake['body'][:-1]:
            return False

        # prevent running into boarders
        x = pos_next['x']
        y = pos_next['y']
        if x < 0 or x > data['board']['width'] - 1 or y < 0 or y > data[
                'board']['height'] - 1:
            return False

        # move seems to be legal
        return True

    def next_position(self, data, move):
        head = dict(data['you']['head'])
        if move == "up":
            head['y'] = head['y'] + 1
        if move == "down":
            head['y'] = head['y'] - 1
        if move == "left":
            head['x'] = head['x'] - 1
        if move == "right":
            head['x'] = head['x'] + 1
        return head

    def next_estimated_data(self, data, move):
        # doesn´t incorporate food
        est = copy.deepcopy(data)
        est['you']['head'] = self.next_position(data, move)
        est['you']['body'] = [est['you']['head']]+est['you']['body'][:-1]
        return est

    def show_input(self, data):
        # this function can be used to display the input data in a more structured way
        for ev in data:
            print(ev, ':')
            if isinstance(data[ev], dict):
                for k, v in data[ev].items():
                    print(' - ', k, ": ", v)
            else:
                print(' - ', data[ev])


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update({
        "server.socket_port":
        int(os.environ.get("PORT", "8080")),
    })
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
