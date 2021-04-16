
/*
    Updates the list of members and the member count with the new list
*/
function updateMembers(members) {
    let memberList = $("#memberList");
            
    // clear the list of members
    memberList.empty();
    
    members.forEach(member => {    
        // add all members back
        memberList.append(`<li>${member.name}</li>`);
    });
    
    $("#current_member_count").text(`${members.length}`); 
}


function establishConnection() {
    $(document).ready(() => {
        let socket = io.connect("http://192.168.188.36:5000");
                
        let username = "";
        let roomId = 0;
        
        socket.on("meta", (data) => {
            username = data.username;
            roomId = data.roomId;
        
            socket.emit("join", { room: roomId });
        });

        socket.on("connect", () => {});

        socket.on("memberChange", (memberList) => {
            updateMembers(memberList.members);
        });
    });
}

establishConnection();