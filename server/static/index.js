
(() => {
function load() {
    let currentState = "spectating";
    
    let sid = "";
    let pokemonName = "";
    let timerTask = null;

    $("#username-wrapper").hide();
    $("#roomId-wrapper").hide();

    const canvas = new DrawingBoard.Board("canvas", {webStorage: false});

    // add disable and enable methods to the canvas object
    canvas.disable = () => {
        $("#canvas").css("pointer-events", "none");
    };

    canvas.enable = () => {
        $("#canvas").css("pointer-events", "")
    };
 
    canvas.disable();

    const sio = io();
   
    $("#chat-input").keypress((e) => {
        const key = e.which;
        const ENTER_KEY_CODE = 13;

        if(key == ENTER_KEY_CODE)  
         {
           sendChatMsg(sio);
           return false;  
         }
    });

    sio.on("connect", () => {
        console.log("connected");

        sio.emit("get_sid", "", (sid_) => { 
            sid = sid_; 
            console.log("Got sid " + sid);
        });
    });

    sio.on("disconnect", () => {
        console.log("disconnected");
    });

    sio.on("room_member_change", (data) => updateMembers(data.members));

    sio.on("msg", (data) => {
        if(data.username !== undefined) {
            $("#chat").append(`<p id="chat-msg"><strong id="chat-msg-username">${data.username}</strong>: ${data.msg}</p>`)
        } else {
            $("#chat").append(`<p id="chat-system-msg">${data.msg}</p>`)
        }
    });

    sio.on("img", (data) => {
        if(currentState != "drawing")
            canvas.setImg(base64Decompress(data));
    });

    sio.on("deltaTime", (data) => {
        // update display
        $("#timer").text(`Timer: ${Math.floor(parseFloat(data.len) - parseFloat(data.deltaTime))}`);
    });

    sio.on("start_round", (data) => {
        deltaTime = 0.0;
        // update memberlist icons

        // clear canvas
        canvas.reset();

        // set state
        if(data.drawing_player === sid) { 
            currentState = "drawing";
            $("#name").text(data.pokemon.name);
            canvas.enable();

            timerTask = setInterval(() => {
                const imgData = base64Compress(canvas.getImg());
                sio.emit("img", imgData);        
            }, 1000);
        } else {
            currentState = "guessing";
            $("#name").text("_ ".repeat(data.pokemon.name.length));
            canvas.disable();
        }
    });

    sio.on("end_of_round", (data) => {
        deltaTime = 0.0;
        // show information about round

        // clear the interval timer
        if(timerTask !== null) {
            clearInterval(timerTask);
            timerTask = null;
        }
    });
    
    sio.on("end_of_game", (data) => {
        // show winners
    });


    $("#login").on("click", () => login(sio));

    $("#join").on("click", () => join(sio));

    $("#start").on("click", () => {
        sio.emit("start", "", (err) => {
            if(err !== "") alert(err);
        });
    });
}

function usernameFormToggle(hide=true, name) {
    if(hide) {
        $("#username_form").hide();
        
        $("#username-wrapper").show();
        $("#username").text(name);
    } else {
        $("#username_form").show();
        $("#username-wrapper").hide();
    }
}

function roomFormToggle(hide=true, roomId, new_room) {
    if(hide) {
        $("#room-form").hide();

        $("#roomId").text(roomId);
        $("#roomId-wrapper").show();
    } else {
        $("#room-form").show();
    }
}

function login(sio) {
    let name = $("#user_name").val();
        
    if(name.length < 3) alert("Name should be at least 3 characters long");
    else sio.emit("login", {name: name}, (res) => {
        if(res) {
            usernameFormToggle(true, name); 
        }
        else {
            alert("Couldn't log into server!");
        }
    })
}

function join(sio) {
    let roomId = $("#room_id").val();
    
    if(roomId === "") roomId = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5);
    
    sio.emit("join", {roomId: roomId}, (res) => {
        if(res.success) {
            roomFormToggle(true, res.roomId, res.new_room);
        } else {
            alert(res.reason);
        }
    });
}

function updateMembers(members) {
    const memberList = $("#member-list");

    memberList.empty();

    members.forEach(member => {
        if (member.leader) memberList.append(`<li>${member.name} ????</li>`);
        else memberList.append(`<li>${member.name}</li>`);
    });
}

function sendChatMsg(sio) {
    const msg = $("#chat-input").val();
    $("#chat-input").val("");

    if(/\S/.test(msg)) sio.emit("message", msg);
}

function base64Compress(imgCur) {
    let compressedImg = imgCur.split('').reduce((o, c) => {
        if (o[o.length - 2] === c && o[o.length - 1] < 35) o[o.length - 1]++;
        else o.push(c, 0);
        return o;
    },[]).map(_ => typeof _ === 'number' ? _.toString(36) : _).join('');

    return compressedImg;
}

function base64Decompress(compressedImgCur) {
    let decompressedImgCur = compressedImgCur
    .split('').map((c,i,a)=>i%2?undefined:new Array(2+parseInt(a[i+1],36)).join(c)).join('');

    return decompressedImgCur;
}

load();

})();