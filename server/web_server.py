import socketio

from serverhandler.serverHandler import ServerHandler
from serverhandler.player import Player

sio = socketio.Server()
app = socketio.WSGIApp(sio, 
    static_files = {
        "/": "./static/"
    }
)

serverhandler = ServerHandler()

@sio.event
def connect(sid, environ): # sid: session id, environ: dict containing client request details 
    print(f"New user ({sid}) connected")

@sio.event
def disconnect(sid):
    print(f"Client ({sid}) disconnected")

@sio.event
def login(sid, data):
    # login new user with given user name
    print(f"Trying to log in a new user with ({sid})")    

    # make sure players can only log in once
    if serverhandler.get_player_by_sid(sid) == None:
        serverhandler.add_player(Player(sid, data["name"], None))
        return True
    else:
        return False

@sio.event
def join(sid, data):
    print(f"User ({sid}) wants to join a room with id ({data['roomId']})")

    # if player not logged in -> error
    if not serverhandler.check_player_login(sid):
        return { "success": False, "reason": "User is not logged in yet!" }

    # if the player is logged in -> put him into the sio room and serverhandler room
    room = serverhandler.get_room_by_id(data["roomId"])    

    sio.enter_room(sid, data["roomId"])

    if room == None:
        # create a new room and put player as leader
        new_room = serverhandler.create_room("", 20, sid, data["roomId"])

        return { "success": True, "roomId": new_room.roomId, "new_room": True }
    else:
        # put player into existing room
        serverhandler.add_player_to_room(sid, data["roomId"])

        sio.emit("room_member_change", room.get_member_list(), to=room.roomId)
        return { "success": True, "roomId": room.roomId, "new_room": False }
    