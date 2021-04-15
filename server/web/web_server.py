from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from uuid import uuid4

# path stuff bc the player file is in parent folder and relative paths don't work with python3 imports
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from player import Player
from main import serverHandler

app = Flask(__name__)
app.secret_key = str(uuid4())

@app.route("/")
def hello_world():
    return render_template("index.html")

# display the room and the members of the room and prompt login if player isn't logged in
@app.route("/rooms/<roomId>", methods=["GET", "POST"])
def room(roomId=None):
    # room doesn't exist yet
    room = serverHandler.get_room_by_id(roomId)
    player = get_player()

    if room == None:
        return redirect(url_for("roomCreate", roomId=roomId))

    # if usr has clicked submit button or is already logged in
    if request.method == "POST" or player != None:
        
        if player == None:
            # create new player instance and save it in session
            name = request.form["usr_name"]
            login_player(name, roomId)
        
        return render_template("room.html", room=room, player=player)
    # new player
    else:
        return render_template("room.html", room=room, player=None)

# create a new room and login player if he hasn't yet
@app.route("/rooms/<roomId>/create", methods=["GET", "POST"])
def roomCreate(roomId):
    player = get_player()
    
    if request.method == "POST":
        # create a new room and login the player if need be
        if player == None:
            name = request.form["usr_name"]
            player = login_player(name, roomId)
        
        max_players = request.form["max_players"]
        room_name = request.form["room_name"]
        
        # create a new room
        serverHandler.create_room(room_name, max_players, player, roomId)
        
        # redirect to the new room page
        return redirect(url_for("room", roomId=roomId)) 

    else:
        return render_template("create_room.html", id=roomId, player=player)

def login_player(name, roomId):
    player = Player(request.remote_addr, name, str(uuid4()), None) # create a new player object
    session["player"] = player
    serverHandler.add_player(player, roomId)

    return player

def get_player():
    return session["player"] if "player" in session else None

# get all member names of a existing room else empty json object
@app.route("/rooms/<roomId>/members")
def roomMembers(roomId=None):
    room = serverHandler.get_room_by_id(roomId)
    
    member_names = room.get_member_names() if room != None else {}

    return jsonify(member_names)


##### SOCKET IO SECTION #####

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def connected():
    print('New user ' + request.remote_addr)

"""
@socketio.on("join")
def join(data):
    print(f"User: {request.remote_addr}")
    join_room(data["room"])
    send({event: "join_player", username: data["username"]})

@socketio.on("leave")
def leave(data):
    pass
"""

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
    