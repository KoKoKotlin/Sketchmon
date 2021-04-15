from room import Room

class ServerHandler:
    def __init__(self):
        self.player = []
        self.rooms = []
    
    def add_player(self, player, roomId):
        for room in self.rooms:
            if room.roomId == roomId:
                room.add_player(player)
    
    def get_room_by_id(self, roomId):
        print(self.rooms)
        for room in self.rooms:
            if room.roomId == roomId: return room
        
        return None
    
    def create_room(self, name, max_players, leader, roomId):
        room = Room(name, max_players, leader, roomId)
        self.rooms.append(room)
    
