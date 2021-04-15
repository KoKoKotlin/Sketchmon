from uuid import uuid4

"""
    class, that handles a game
    contains round information and player information
"""
class Room:

    def __init__(self, name, max_players, leader, roomId):
        self.name = name                    # display name of the room
        self.players = [leader]              # all players currently in the room
        self.leader = leader                # room leader that can change settings
        self.active_player = []             # players that are currently playing and not spectating
        self.rounds = 0                     # round counter
        self.max_players = max_players      # maximum amount of players the room can have
        self.game_state = GAME_STATES[1]    # current state of the room
        self.roomId = roomId                # unique id for the room

    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)

    def get_member_names(self):
        return {"members": [player.name for player in self.players]}

GAME_STATES = ["playing", "waiting"]