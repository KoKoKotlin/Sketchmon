from room import Room

class ServerHandler:
    def __init__(self):
        self.players = []
        self.rooms = []
    
    def add_player(self, player, roomId):
        print(f"Add player {player} to room {roomId}")

        if player not in self.players: self.players.append(player)

        for room in self.rooms:
            if room.roomId == roomId:
                room.add_player(player)
    
    def get_room_by_id(self, roomId):
        for room in self.rooms:
            if room.roomId == roomId: return room
        
        return None
    
    def create_room(self, name, max_players, leader, roomId):
        room = Room(name, max_players, roomId)
        
        room.add_player(leader)
        room.leader = leader
        
        print(f"Create a new room {room} and leader {leader}")
        
        self.rooms.append(room)
    
    def get_player_by_ip(self, player_ip):
        for player in self.players:
            if player.ip == player_ip: return player
        
        return None
    
    def remove_player(self, player, roomId):
        print(f"Remove player {player} from room {room}")

        # remove the player from the room
        for room in self.rooms:
            if room.id == roomId: 
                room.remove_player(player)
                
                # if the room is empty -> delete it
                if len(room.players) == 0:
                    print(f"Room {roomId} is now empty. Deleting...")
                    self.rooms.remove(room)
                

    def delete_player(self, player):
        print(f"Deleting player {player}")
        self.players.remove(player)
    
    def handle_disconnect(self, player):
        print(f"Handle disconnect of player {player}")

        for room in self.rooms:
            if player in room.players:
                room.remove_player(player)

        self.delete_player(player)