const express = require("express");
const http = require("http");
const socketio = require("socket.io");
const app = express();
const server = http.Server(app);
const io = socketio(server);
const fs = require('fs');
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
    res.sendFile(__dirname + "/pbl.html");
});

app.use(express.static(__dirname));

server.listen(PORT, () => {
    console.log("server on port %d", PORT);
});

io.on("connection", (socket) => {
    console.log("connection: ", socket.id);
    console.log("run fs.watch");
    socket.emit("first_send", "");
    fs.watch(__dirname + "/data.json", {persistent: true}, function(){
        socket.emit("send_json", "");
    });
});