from serverhandler.room import Room

class ServerHandler:
    def __init__(self, sio):
        self.players = []
        self.rooms = []
        self.sio = sio
    
    def add_player(self, player):
        print(f"Login a new player {player}")

        self.players.append(player)
    
    def add_player_to_room(self, sid, roomId):
        player = self.get_player_by_sid(sid)
        room = self.get_room_by_id(roomId)
        
        print(f"Adding player ({player}) to room ({room})")
        
        room.add_player(player)

    def get_player_by_sid(self, player_sid):
        for player in self.players:
            if player.sid == player_sid: return player
        
        return None
    
    def handle_disconnect(self, sid):
        player = self.get_player_by_sid(sid)

        # if the player was logged in
        if player != None:
            print(f"Handle disconnect of player {player}")

            for room in self.rooms:
                if player in room.players:
                    room.remove_player(player)

                    if room.is_empty():
                        print(f"Room ({room.roomId}) is empty. Deleting...")
                        self.rooms.remove(room)

            self.delete_player(player)
    
    def check_player_login(self, sid):
        return self.get_player_by_sid(sid) != None

    def delete_player(self, player):
        print(f"Deleting player {player}")
        self.players.remove(player)
    
    def create_room(self, name, max_players, sid, roomId):
        leader = self.get_player_by_sid(sid)
        room = Room(name, max_players, roomId, self.sio)
        
        room.add_player(leader)
        room.leader = leader
        
        print(f"Create a new room {room} with leader {leader}")
        
        self.rooms.append(room)
        
        return room
    
    def get_room_by_id(self, roomId):
        for room in self.rooms:
            if room.roomId == roomId: return room
        
        return None
    
    def get_room_by_player(self, sid):
        player = self.get_player_by_sid(sid)

        if player == None:
            return None

        return player.roomId

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
