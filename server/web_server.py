import socketio
import html

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

    # handle player disconnect
    roomId = serverhandler.get_room_by_player(sid)
    serverhandler.handle_disconnect(sid)
    
    notify_member_change(roomId)

@sio.event
def login(sid, data):
    # login new user with given user name
    print(f"Trying to log in a new user with ({sid})")    

    # make sure players can only log in once
    if serverhandler.get_player_by_sid(sid) == None:
        serverhandler.add_player(Player(sid, escape_user_input(data["name"]), None))
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
    room = serverhandler.get_room_by_id(escape_user_input(data["roomId"]))    

    # put player into sio room
    sio.enter_room(sid, escape_user_input(data["roomId"]))

    # create room for the game logic
    if room == None:
        # create a new room and put player as leader
        new_room = serverhandler.create_room("", 20, sid, escape_user_input(data["roomId"]))
        
        notify_member_change(new_room.roomId)
        return { "success": True, "roomId": new_room.roomId, "new_room": True }
    else:
        # put player into existing room
        serverhandler.add_player_to_room(sid, escape_user_input(data["roomId"]))

        notify_member_change(room.roomId)
        return { "success": True, "roomId": room.roomId, "new_room": False }

@sio.event
def message(sid, data):
    print(f"User ({sid}) wants to send msg ({data})")

    # check if player is logged in and has joined a room
    if (player := serverhandler.get_player_by_sid(sid)) != None \
   and (roomId := serverhandler.get_room_by_player(sid)) != None:
        print(f"Broadcasting msg ({data}) of player ({player}) to room ({roomId})")
        sio.emit("msg", {"username": player.name, "msg": escape_user_input(data)}, to=roomId)

def notify_member_change(roomId):
    room = serverhandler.get_room_by_id(roomId)
    sio.emit("room_member_change", room.get_member_list(), to=room.roomId)

def escape_user_input(msg):
    return html.escape(msg)