from uuid import uuid4
from random import choice

from threading import Thread
import time

from serverhandler.pokeapi.api import get_random_pokemon

class Round:
    ROUND_TIME = 100                        # time in seconds a round lasts
    AFTER_ROUND_TIME = 10                   # time the results of the last round are shown

    STATES = ["round", "after_round", "start", "end"]

    def __init__(self, room, sio):
        self.room = room                    # room that is currently playing

        self.drawer = 0                     # index of the currently drawing player

        self.current_pokemon = None         # pokemon that should be drawn in the current round

        self.state = "start"                # state the room is currently in
        
        self.sio = sio

    def start(self):
        # reset the meta information of the round
        self.drawer = 0

        start_time = 0        # time the current state has started
        while True:
            if self.state == "start":
                self.start_new_round()
                start_time = time.time()
            
            if self.state == "end":
                break

            delta_time = (time.time() - start_time)
            if self.state == "round":
                if delta_time >= self.ROUND_TIME:
                    # end the current round
                    self.end_round()
                    start_time = time.time()
                    continue
                else:
                    # send the current delta_time
                    self.sio.emit("deltaTime", {"deltaTime": str(delta_time), "len": self.ROUND_TIME, "state": self.state}, to=self.room.roomId)
            
            
            if self.state == "after_round":
                if delta_time >= self.AFTER_ROUND_TIME:
                    # start next round or end game
                    self.drawer += 1
                    if self.drawer >= len(self.room.players):
                        self.end_game()
                    else:
                        self.start_new_round()
                        start_time = time.time()
                        continue
                else:
                    # send the current delta_time
                    self.sio.emit("deltaTime", {"deltaTime": str(delta_time), "len": self.AFTER_ROUND_TIME, "state": self.state}, to=self.room.roomId)

            time.sleep(1)
    
    def start_new_round(self):
        # send new_round info
        drawing_player = self.room.players[self.drawer]
        self.current_pokemon = get_random_pokemon()

        data = {
            "drawing_player": drawing_player.sid,
            "pokemon": self.current_pokemon
        }

        self.sio.emit("start_round", data, to=drawing_player.roomId)

        # set the correct state
        self.state = self.STATES[0]
    
    def end_round(self):
        drawing_player = self.room.players[self.drawer]
        
        data = {
            "drawing_player": drawing_player.sid, 
            "pokemon": self.current_pokemon,
            "list_of_winners": []
        }

        self.sio.emit("end_of_round", data, to=self.room.roomId)
        
        self.state = self.STATES[1]
    
    def end_game(self):
        data = {}

        self.sio.emit("end_of_game", data, to=self.room.roomId)
        
        self.state = self.STATES[3]
    
"""
    class, that handles a game
    contains round information and player information
"""
class Room:

    def __init__(self, name, max_players, roomId, sio):
        self.name = name                    # display name of the room
        self.players = []                   # all players currently in the room
        self.leader = None                  # room leader that can change settings
        self.active_player = []             # players that are currently playing and not spectating
        self.rounds = 0                     # round counter
        self.max_players = max_players      # maximum amount of players the room can have
        self.game_state = GAME_STATES[1]    # current state of the room
        self.roomId = roomId                # unique id for the room

        self.round = None                   # controls the current round
        self.sio = sio


    def add_player(self, player):
        player.roomId = self.roomId
        
        if player not in self.players:
            self.players.append(player)

    def remove_player(self, player):
        player.current_room = None

        if player.sid == self.leader.sid and len(self.players) > 1:
            self.leader = choice(self.players)
            print(f"The leader disconnected. Setting new leader to ({self.leader})")
            
        self.players.remove(player)

    def get_member_list(self):
        return {"members": [{"name": player.name, "leader": player == self.leader} for player in self.players]}
    
    def is_full(self):
        return len(self.players) >= self.max_players

    def is_empty(self):
        return len(self.players) == 0

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', roomId='{self.roomId}', leader='{self.leader.name}')"

    def start(self):
        print(f"Starting game in room ({self.roomId})")
        self.round = Round(self, self.sio)
        self.sio.start_background_task(self.round.start)

GAME_STATES = ["playing", "waiting"]