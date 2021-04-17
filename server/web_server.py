from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from uuid import uuid4

from serverhandler.player import Player
from serverhandler.serverHandler import ServerHandler

app = Flask(__name__)
app.secret_key = str(uuid4())       # TODO: generate real secret key and put in env var

socketio = SocketIO(app, manage_session=False, cors_allowed_origins="*")

serverHandler = ServerHandler()

@app.route("/")
def index():
    return render_template("index.html", player=get_player())

# route for getting a user name
@app.route("/login", methods=["GET", "POST"])
def login():
    player = get_player()
    
    if request.method == "POST":
        name = request.form["usr_name"]

        if len(name) <= 2:
            return render_template("login.html")
        else:
            session["player"] = Player(request.remote_addr, name, None)
            return redirect(url_for("index"))

    if player == None:
        return render_template("login.html")
    else:
        return redirect(url_for("index"))

# display the room and the members of the room and prompt login if player isn't logged in
@app.route("/rooms/<roomId>")
def room(roomId=None):
    # room doesn't exist yet
    room = serverHandler.get_room_by_id(roomId)
    player = get_player()
    
    if player == None:
        return redirect(url_for("login"))

    if room == None:
        return redirect(url_for("roomCreate", roomId=roomId))
    else:
        return render_template("room.html", room=room, player=player, members=None)

# create a new room and login player if he hasn't yet
@app.route("/rooms/<roomId>/create", methods=["GET", "POST"])
def roomCreate(roomId):
    player = get_player()
    
    if player == None:
        return redirect((url_for("login")))
    
    if request.method == "POST":
        # create a new room 
        max_players = int(request.form["max_players"])
        room_name = request.form["room_name"]
        
        # create a new room
        serverHandler.create_room(room_name, max_players, player, roomId)
        
        # redirect to the new room page
        return redirect(url_for("room", roomId=roomId)) 

    else:
        return render_template("create_room.html", id=roomId, player=player)

def get_player():
    return session["player"] if "player" in session and session["player"] != None else None

##### SOCKET IO SECTION #####

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
    