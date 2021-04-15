from dataclasses import dataclass
from room import Room

@dataclass(frozen=False, init=True)
class Player:
    ip: str                 # ip addr of player with which he is connected to the server
    name: str               # display name of a player
    player_uuid: str        # unique identifier so that players can have the same name
    current_room: Room      # room the player is currently in
