from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from uuid import uuid4

from serverhandler.player import Player
from serverhandler.serverHandler import ServerHandler

app = Flask(__name__)
app.secret_key = str(uuid4())

serverhandler = ServerHanlder()

@app.route("/")
def hello_world():
    return render_template("index.html")

# display the room and the members of the room and prompt login if player isn't logged in
@app.route("/rooms/<roomId>")
def room(roomId=None):
    # room doesn't exist yet
    room = serverHandler.get_room_by_id(roomId)
    player = get_player()

    if room == None:
        return redirect(url_for("roomCreate", roomId=roomId))
    
    if player != None:
        return render_template("room.html", room=room, player=player, members=None)
    else:
        return redirect(url_for("roomLogin", roomId=roomId))

@app.route("/rooms/<roomId>/login", methods=["GET", "POST"])
def roomLogin(roomId):
    # if usr has clicked submit button or is already logged in
    room = serverHandler.get_room_by_id(roomId)
    
    if room.is_full():
        members = room.get_member_names()["members"]
        return render_template("room_full.html", room=room, members=members)
    
    if request.method == "POST":
        name = request.form["usr_name"]        
        login_player(name, roomId)
        return redirect(url_for("room", roomId=roomId))
    
    members = serverHandler.get_room_by_id(roomId).get_member_names()["members"]
    return render_template("room.html", room=room, player=None, members=members)


def onPlayerJoinRoom():
    socketio.send()

# create a new room and login player if he hasn't yet
@app.route("/rooms/<roomId>/create", methods=["GET", "POST"])
def roomCreate(roomId):
    player = get_player()
    
    if request.method == "POST":
        # create a new room and login the player if need be
        if player == None:
            name = request.form["usr_name"]
            player = login_player(name, roomId)
        
        max_players = int(request.form["max_players"])
        room_name = request.form["room_name"]
        
        # create a new room
        serverHandler.create_room(room_name, max_players, player, roomId)
        
        # redirect to the new room page
        return redirect(url_for("room", roomId=roomId)) 

    else:
        return render_template("create_room.html", id=roomId, player=player)

def login_player(name, roomId):
    player = Player(request.remote_addr, name, None) # create a new player object
    serverHandler.add_player(player, roomId)

    return player

def get_player():
    return serverHandler.get_player_by_ip(request.remote_addr)

# get all member names of a existing room else empty json object
@app.route("/rooms/<roomId>/members")
def roomMembers(roomId=None):
    room = serverHandler.get_room_by_id(roomId)
    
    member_names = room.get_member_names() if room != None else {}

    return jsonify(member_names)


##### SOCKET IO SECTION #####

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def connected():
    print("New user connected!")
    player = serverHandler.get_player_by_ip(request.remote_addr)

    emit("meta", {"username": player.name, "roomId": player.current_room.roomId})

@socketio.on("join")
def join(data):
    player = serverHandler.get_player_by_ip(request.remote_addr)
    
    print(f"User ({player.name}) successfully joined room with id ({data['room']})")
    join_room(data["room"])

    emit("memberChange", serverHandler.get_room_by_id(data["room"]).get_member_names())

@socketio.on("disconnect")
def leave():
    player = get_player()
    print(f"Player left: {player}")
    
    serverHandler.handle_disconnect(player)
    
if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
    