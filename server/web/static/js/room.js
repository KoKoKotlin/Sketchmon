/*
    Updates the list of members while waiting for the room to fill up
*/
function updateMembers() {
    const baseUrl = window.location;

    fetch(baseUrl.pathname + "/members").then((resp) => {
        resp.json().then(json => {
            
            let memberList = $("#memberList");
            
            // clear the list of members
            memberList.empty();
            
            
            json.members.forEach(member => {    
                // add all members back
                memberList.append(`<li>${member}</li>`);
            });
            
            $("#current_member_count").text(`${json.members.length}`); 
        })
    });   
}

function establishConnection() {
    $(document).ready(() => {
        let socket = io.connect("http://192.168.188.36:5000");
        
        socket.on('connect', () => {
            socket.emit('first', {data: 'I\'m connected!'});
        });
    });
}

establishConnection();

setInterval(updateMembers, 2000);