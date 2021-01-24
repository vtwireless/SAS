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

    socket.on("doit", (data) => {
        console.info(data);
        socket.emit("doIt");
        console.info("sent");
    });

    // ###################################
    // # WinnForum Defined Functionality #
    // ###################################
    //          As listed in Table 1
    socket.on("registrationRequest", (data) => {
        console.info("Receiving Data: " + (data));
        var payload = JSON.stringify({registrationResponse: [{
            cbsdInfo: "CBSDIDNo12",
            measReportConfig: ["CONFIG_A"],
            response: {
                responseCode: "0",
                responseMessage: "Test message",
                responseData: "data"
            } 
        }]});
        socket.emit("registrationResponse", payload)
    });

    socket.on("spectrumInquiryRequest", (data) => {
        console.info("Receiving Data: " + JSON.stringify(data));
        var payload = JSON.stringify({spectrumInquiryRequest: [{
            // No need to bother with response
        }]});
    });

    socket.on("grantRequest", (data) => {
        console.info("Grant Request Data: " + data);
    });

    socket.on("heartbeatRequest", (data) => {
        console.info("Heartbeat Request Data: " + data);
    });

    socket.on("relinquishmentRequest", (data) => {
        console.info("Relinquishment Request Data: " + data);
    });

    socket.on("deregistrationRequest", (data) => {
        console.info("Deregistration Request Data: " + data);
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
