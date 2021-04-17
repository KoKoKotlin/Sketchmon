(() => {
function load() {
    $("#username-wrapper").hide();
    $("#roomId-wrapper").hide();

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
    });

    sio.on("disconnect", () => {
        console.log("disconnected");
    });

    sio.on("room_member_change", (data) => updateMembers(data.members));

    sio.on("msg", (data) => {
        if(data.username !== "") {
            $("#chat").append(`<p><strong>${data.username}</strong>: ${data.msg}</p>`)
        } else {
            $("#chat").append(`<p style="color: red;">${data.msg}</p>`)
        }
    });

    $("#login").on("click", () => login(sio));

    $("#join").on("click", () => join(sio));
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
        if (member.leader) memberList.append(`<li>${member.name} 👑</li>`);
        else memberList.append(`<li>${member.name}</li>`);
    });
}

function sendChatMsg(sio) {
    const msg = $("#chat-input").val();
    $("#chat-input").val("");

    sio.emit("message", msg);
}

load();

})();