document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "192.168.86.165";   // the IP address of your Raspberry PI
var streamIntervalId = 0;

function client(){
    var input = document.getElementById("message").value;
    send_data(input);
}

function send_data(input) {
    const net = require('net');
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        //console.log('connected to server!');
        // send the message
        client.write(`${input}\r\n`);
    });
    
    // get the data from the server
    client.on('data', (data) => {
        let str = data.toString().trim();
        console.log(str);

        let arr = str.split(',');
        document.getElementById("direction").innerHTML = arr[0];
        document.getElementById("speed").innerHTML = arr[1];
        document.getElementById("distance").innerHTML = arr[2];
        document.getElementById("temperature").innerHTML = arr[3];
        
        client.end();
        client.destroy();
    });

    // client.on('end', () => {
    //     console.log('disconnected from server');
    // });


}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_data("87");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_data("83");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        send_data("65");
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        send_data("68");
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";

    send_data("88");
}


// update data for every 500ms
function start_streaming(){
    streamIntervalId = setInterval(function(){
        // get image from python server
        client();
    }, 500);
}

function stop_streaming() {
    clearInterval(streamIntervalId);
}