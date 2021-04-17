import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio, 
    static_files = {
        "/": "./static/"
    }
)

@sio.event
def connect(sid, environ): # sid: session id, environ: dict containing client request details 
    print(f"New user ({sid}) connected")

@sio.event
def disconnect(sid):
    print(f"Client ({sid}) disconnected")