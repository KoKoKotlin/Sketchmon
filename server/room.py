from uuid import uuid4
from random import choice

"""
    class, that handles a game
    contains round information and player information
"""
class Room:

    def __init__(self, name, max_players, roomId):
        self.name = name                    # display name of the room
        self.players = []                   # all players currently in the room
        self.leader = None                  # room leader that can change settings
        self.active_player = []             # players that are currently playing and not spectating
        self.rounds = 0                     # round counter
        self.max_players = max_players      # maximum amount of players the room can have
        self.game_state = GAME_STATES[1]    # current state of the room
        self.roomId = roomId                # unique id for the room

    def add_player(self, player):
        player.current_room = self
        
        if player not in self.players:
            self.players.append(player)

    def remove_player(self, player):
        player.current_room = None

        if player == self.leader:
            leader = choice(self.players)

        self.players.remove(player)

    def get_member_names(self):
        return {"members": [(player.name, player == self.leader) for player in self.players]}
    
    def is_full(self):
        return len(self.players) >= self.max_players

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', roomId='{self.roomId}, leader={self.leader.name}')"

GAME_STATES = ["playing", "waiting"]