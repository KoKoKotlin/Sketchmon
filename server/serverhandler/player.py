from dataclasses import dataclass
from serverhandler.room import Room

@dataclass(frozen=False, init=True)
class Player:
    ip: str                 # ip addr of player with which he is connected to the server
    name: str               # display name of a player
    room_id: str            # room id of the room the player is currently in