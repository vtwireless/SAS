const
io = require("socket.io"),
server = io.listen(5000);

let seqNum = new Map();

var startUpCommands = {
    command: 'START',
    dB: 100,
    frequency: 915000,
    bandwidth: 100
}

var shutDownCommands = {
    
}

server.on("connection", (socket) => {
    console.info("IP Address: " + socket.handshake.address);
    seqNum.set(socket, 1);
    socket.emit("identifySource");

    socket.on("identifySource", (data) => {
        console.info(data);
        // check if in database
        // if yes use params and go
        // if not, go to registration
       
    });

    socket.on("createNode", (data) => {
        console.info(data);
    });

    // ###################################
    // # WinnForum Defined Functionality #
    // ###################################
    //          As listed in Table 1
    socket.on("registrationRequest", (data) => {
        console.info("Receiving Data: " + (data));
        // var payload = JSON.stringify({registrationResponse: [{
        //     cbsdInfo: "CBSDIDNo12",
        //     measReportConfig: ["CONFIG_A"],
        //     response: {
        //         responseCode: "0",
        //         responseMessage: "Test message",
        //         responseData: "data"
        //     } 
        // }]});
        socket.emit("registrationResponse", JSON.stringify("SASResponse"))
    });

    socket.on("spectrumInquiryRequest", (data) => {
        console.info("Receiving Data: " + (data));
   
        socket.emit("spectrumInquiryResponse", JSON.stringify("SASResponse"))
    });

    socket.on("grantRequest", (data) => {
        console.info("Grant Request Data: " + data);
        socket.emit("grantResponse", JSON.stringify("you did a grant thing"));

    });

    socket.on("heartbeatRequest", (data) => {
        console.info("Heartbeat Request Data: " + data);
        socket.emit("heartbeatResponse", JSON.stringify("you did a heartbeat thingy"))
    });

    socket.on("relinquishmentRequest", (data) => {
        console.info("Relinquishment Request Data: " + data);
    });

    socket.on("deregistrationRequest", (data) => {
        console.info("Deregistration Request Data: " + data);
        socket.emit("deregistrationResponse", JSON.stringify("repinseadfsdf"))

    });
    //  end official functions--------------------------------

    socket.on("getTxParams", (data) => {
        console.info("Receiving TX Params: " + data);
        socket.emit("getRxParams")
    });

    socket.on("getRxParams", (data) => {
        console.info("Receiving Rx Params: " + data);
    });
    
    socket.on("disconnect", () => {
        socket.emit("shutDown", shutDownCommands);
        seqNum.delete(socket);
    });

});
