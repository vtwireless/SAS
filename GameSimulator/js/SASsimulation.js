var myTime;
var nowLine;
var canvasWidth = 1200;
var canvasHeight = 700;
var myGrants = [];
var requestList = [];
var finalGrantList = [];
var approvedGrants = [];
var approvedRequests = [];

var approvedGrantCount = 0;
var deniedGrantCount = 0;
var cancelledGrantCount = 0;
var movedGrantCount = 0;
var grantSummaryText;
var summaryTextHeight = 100;
var bandwidthBox;
var frequencyRange = 1500;//35500-37000
var titleOffset = 50;
var baseFrequency = 35500;
var nowLinePosition = 200;
var movingTexts = [];
var frequencyTexts = [];
var stopTime = 5000;

var seedValue = 3;
var isPaused = false;

// holds array of grant data
var setSeed;

/**
 * Popup box component 
 *
 * @type {component}
 */
var popupBox = new component(
    600,
    300,
    "grey",
    300,
    150,
    "popup"
);
popupBox.title = "popupBox";
popupBox.freqText1 = "Freq1";
popupBox.freqText2 = "Freq2";
popupBox.startTime = "startTime";
popupBox.lenStr = "lenStr";

var popupBoxGrant;

var popupOpened = false;

// ! codemirror
var editor = CodeMirror.fromTextArea(
    document.getElementById("code"), {
    lineNumbers: true,
    styleActiveLine: true,
    matchBrackets: true,
    spellcheck: true,
    autocorrect: true,
    autocapitalize: true,
    rtlMoveVisually: true,
    scrollbarStyle: "overlay",
    theme: "blackboard",
    resize: "vertical",
    mode: { name: "javascript", globalVars: true }
}
);

// listen for the beforeChange event, test the changed line number, and cancel
editor.on('beforeChange', function (cm, change) {
    if (~[0, editor.getDoc().size - 1].indexOf(change.from.line)) {
        change.cancel();
    }
});

// ! codemirror
var displayConsole = CodeMirror.fromTextArea(
    document.getElementById("consoleOutput"), {
    styleActiveLine: false,
    matchBrackets: false,
    lineNumbers: false,
    scrollbarStyle: "overlay",
    readOnly: "nocursor",
    theme: "blackboard",
    resize: "vertical",
    mode: { name: "javascript", globalVars: true }
}
);

// resize 
editor.setSize(1000, 200);
displayConsole.setSize(500, 130);


/**
 * Array of rect components representing the requested grants
 * pre-selection
 *
 * @type {component[]}
 */
var queuedGrantRects = [];

/**
 * Rects representing highlighted grants on mouseover
 *
 * @type {component[]}
 */
var hoveredGrant = [];

// load two components into hoveredGrant 
hoveredGrant.push(new component(0, 0, "rgba(0, 128, 255)", 0, 0, "select"));
hoveredGrant.push(new component(0, 0, "rgba(0, 128, 255)", 0, 0, "select"));
hoveredGrant[0].text = "";
hoveredGrant[1].text = "";


// !---------------------- dynamic loading of grant data  -----------------------------!
/**
 * Array of setSeed Filenames
 *
 * @type {String[]}
 */
const setSeedFilenames = [
    "setSeeds/1.csv",
    "setSeeds/2.csv",
    "setSeeds/3.csv"
];

/**
 * Load set seeds from file using papaparse.
 * CSV loading is async, thus a callback function must
 * be passed, which will be executed upon the load
 * 
 * @param {int} seedValue seed number, filename must be {seedValue}.csv
 * @param {function} callback callback function to be executed onload
 */
function loadSetSeed(seedValue, callback) {

    Papa.parse(setSeedFilenames[seedValue - 1], {
        download: true,
        complete: function (results) {
            addCSVToSetSeeds(results, callback);
        },
        header: true,
        dynamicTyping: true
    });


    function addCSVToSetSeeds(csv, callback) {
        var readingRequests = false;
        var PU = [];
        var REQ = [];
        var setSeed = [];

        csv.data.forEach(function (row) {
            if (row.startTime == null) { // empty line means we're now reading requests
                readingRequests = true;
                return; // continue
            }
            readingRequests ? REQ.push(row) : PU.push(row);


        });
        setSeed.PU = PU;
        setSeed.REQ = REQ;
        callback(setSeed); // startGame is called and passed PU + REQ grant creation arguments

    }

}


class Grant {
    constructor(startTime, length, frequency, bandwidth, frequencyb, showTime) {
        this.startTime = startTime;
        this.length = length;
        this.frequency = frequency;
        this.bandwidth = bandwidth;
        this.frequencyb = frequencyb;
        this.showTime = showTime > 0 ? showTime : 1; // if showtime is 0, grants may never be queued
        /** 
         * @type {int} 0 = not yet accepted, 1 = accepted, 2 = conflicting, 3 = denied*/
        this.acceptStatus = 0;
    }
}

var tempGrantComponent = new component(0, 0, "green", 0, 0);

var grantsToShow = [];



function printToOutput(str, newLine = true) {
    if (newLine) {
        displayConsole.setValue(displayConsole.getValue() + "\n" + str);
        displayConsole.scrollTo(null, 10000); // scroll down
        return;
    }
    displayConsole.setValue(displayConsole.getValue() + str);
    displayConsole.scrollTo(null, 10000); // scroll down
}

function clearConsole() {
    displayConsole.setValue("");
}



function startGame(readSeed) {
    setSeed = readSeed;
    nowLine = new component(2, canvasHeight - summaryTextHeight - titleOffset, "red", nowLinePosition, 50);
    grantSummaryText = new component("20px", "Consolas", "black", 150, canvasHeight - 50, "text");
    grantSummaryBox = new component(canvasWidth, summaryTextHeight, "white", 0, canvasHeight - summaryTextHeight);
    bandwidthBox = new component(100, canvasHeight, "white", 0, 0);

    myGrants = [];
    approvedGrants = [];
    approvedRequests = [];
    movingTexts = [];
    frequencyTexts = [];
    grantsToShow = [];
    requestList = [];
    isPaused = false;


    myTime = new component("30px", "Consolas", "black", nowLinePosition, 40, "text");


    clearConsole();
    seedValue != 0 ? printToOutput("Seed " + seedValue + " loaded.", false) : printToOutput("Random Generation Enabled.", false)
    printToOutput("====================================================================");


    myGameArea.start();
}

var myGameArea = {
    canvas: document.createElement("canvas"),
    speed: "1x",
    start: function () {
        if (this.interval) {
            clearInterval(this.interval);
        }
        this.canvas.width = canvasWidth;
        this.canvas.height = canvasHeight;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[5]);
        this.frameNo = 0;
        loadGrantsAndPUs();


        createFrequencyTexts();
        this.isPaused = false;
        this.interval = setInterval(updateGameArea, 20);

    },
    clear: function () {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

// !---------------------- canvas event listeners  -----------------------------!


myGameArea.canvas.onmousemove = function (e) {
    var rect = this.getBoundingClientRect(),
        x = e.clientX - rect.left,
        y = e.clientY - rect.top,
        i = 0,
        r;

    // Dont do anything if popup box is open
    if (popupOpened) {
        // mouseover events during popup can be added here
        // Note this will only work if canvas is not paused

        // Handle hovering over Accept buttons
        if (
            (x > popupBox.x + 20 &&
                x < popupBox.x + 20 + 112 &&
                y > popupBox.y + 132 &&
                y < popupBox.y + 132 + 38)
            ||
            ((x > popupBox.x + 20 &&
                x < popupBox.x + 20 + 112 &&
                y > popupBox.y + 242 &&
                y < popupBox.y + 242 + 38) && grantsToShow[popupBoxGrant].frequencyb > 0) // dont hover over freqb if doesnt exist
        ) {
            var freq = (y > (popupBox.y + 242) && popupBox.freqText2.length > 0) ?
                grantsToShow[popupBoxGrant].frequencyb : grantsToShow[popupBoxGrant].frequency;
            var startFrequency = freq - grantsToShow[popupBoxGrant].bandwidth / 2; // calc start frequency
            var startPlace = frequencyToPixelConversion(startFrequency); // convert startFrequency to pixel coordinates
            var heightOfBlock = bandwidthToComponentHeight(grantsToShow[popupBoxGrant].bandwidth); // calc height of block

            hoveredGrant[0].x = grantsToShow[popupBoxGrant].startTime - myGameArea.frameNo;
            hoveredGrant[0].y = startPlace;
            hoveredGrant[0].width = grantsToShow[popupBoxGrant].length;
            hoveredGrant[0].height = heightOfBlock;
            hoveredGrant[0].text = (baseFrequency + freq) / 10000 + " GHz";
            return;

        }

        // Handle hovering over Deny buttons
        if (x > popupBox.x + 387 &&
            x < popupBox.x + 387 + 183 &&
            y > popupBox.y + 83 &&
            y < popupBox.y + 83 + 183) {
            var startFrequencya = grantsToShow[popupBoxGrant].frequency - grantsToShow[popupBoxGrant].bandwidth / 2; // calc start frequencya
            var startFrequencyb = grantsToShow[popupBoxGrant].frequencyb - grantsToShow[popupBoxGrant].bandwidth / 2; // calc start frequencyb

            var startPlacea = frequencyToPixelConversion(startFrequencya); // convert startFrequencya to pixel coordinates
            var startPlaceb = frequencyToPixelConversion(startFrequencyb); // convert startFrequencyb to pixel coordinates

            var heightOfBlock = bandwidthToComponentHeight(grantsToShow[popupBoxGrant].bandwidth); // calc height of block


            hoveredGrant[0].x = grantsToShow[popupBoxGrant].startTime - myGameArea.frameNo;
            hoveredGrant[0].y = startPlacea;
            hoveredGrant[0].width = grantsToShow[popupBoxGrant].length;
            hoveredGrant[0].height = heightOfBlock;
            hoveredGrant[0].text = "DENY";
            if (grantsToShow[popupBoxGrant].frequencyb > 0) {
                hoveredGrant[1].x = grantsToShow[popupBoxGrant].startTime - myGameArea.frameNo;
                hoveredGrant[1].y = startPlaceb;
                hoveredGrant[1].width = grantsToShow[popupBoxGrant].length;
                hoveredGrant[1].height = heightOfBlock;
                hoveredGrant[1].text = "DENY";
            }



            return;
        }

        hoveredGrant[0].x = 0;
        hoveredGrant[0].y = 0;
        hoveredGrant[0].width = 0;
        hoveredGrant[0].height = 0;
        hoveredGrant[0].text = "";

        hoveredGrant[1].x = 0;
        hoveredGrant[1].y = 0;
        hoveredGrant[1].width = 0;
        hoveredGrant[1].height = 0;
        hoveredGrant[1].text = "";
        return; // all other mousemouse events are ignored when popup box is open
    }
    var grantHovered = false;

    queuedGrantRects.forEach(function (r) {
        if (grantHovered) {
            return;
        }
        if (r.grant.acceptStatus !== 0) {
            return; // dont check for overlap with denied grants
        }
        if (x >= r.x && x <= r.x + r.width && y >= r.y && y <= r.y + r.height) {
            hoveredGrant[0].x = r.x;
            hoveredGrant[0].y = r.y;
            hoveredGrant[0].width = r.width;
            hoveredGrant[0].height = r.height;
            hoveredGrant[0].color = "red";
            grantHovered = true;
            return;
        }
    });

    if (!grantHovered) {
        hoveredGrant[0].x = 0;
        hoveredGrant[0].y = 0;
        hoveredGrant[0].width = 0;
        hoveredGrant[0].height = 0;
        hoveredGrant[0].text = "";

        hoveredGrant[1].x = 0;
        hoveredGrant[1].y = 0;
        hoveredGrant[1].width = 0;
        hoveredGrant[1].height = 0;
        hoveredGrant[1].text = "";

    }

};
// Mouseclick event listener attached to canvas
myGameArea.canvas.onmousedown = function (e) {
    var rect = this.getBoundingClientRect(),
        x = e.clientX - rect.left,
        y = e.clientY - rect.top,
        i = 0,
        r;
    // intercept mouse click on popup box
    if (popupOpened) {
        // on clicking [x] close popup
        if (x > popupBox.x + popupBox.width - 25 &&
            x < popupBox.x + popupBox.width &&
            y > popupBox.y &&
            y < popupBox.y + 25) {
            popupOpened = false;
            if (document.querySelector('input[id="pauseOnPopup"]').checked) {
                play();
            }
        }

        // on clicking Accept1 close popup
        if (x > popupBox.x + 20 &&
            x < popupBox.x + 20 + 112 &&
            y > popupBox.y + 132 &&
            y < popupBox.y + 132 + 38) {
            popupOpened = false;
            console.log("Accept 1 Clicked");
            var overlapCheck = checkOverlap(grantsToShow[popupBoxGrant].startTime, grantsToShow[popupBoxGrant].startTime + grantsToShow[popupBoxGrant].length, grantsToShow[popupBoxGrant].frequency, grantsToShow[popupBoxGrant].bandwidth);
            approvedGrants.push(grantsToShow[popupBoxGrant]);
            grantsToShow[popupBoxGrant].acceptStatus = overlapCheck ? 2 : 1;

            convertGrant(
                grantsToShow[popupBoxGrant],
                false,
                overlapCheck ? "red" : "cyan", // ternary operation for color
                "SU Grant F: " +
                (baseFrequency + grantsToShow[popupBoxGrant].frequency) / 10000 +
                "GHz Bandwidth: " +
                grantsToShow[popupBoxGrant].bandwidth / 10 +
                "MHz"
            );
            printToOutput("Manually accepted " + "SU Grant F: " +
                (baseFrequency + grantsToShow[popupBoxGrant].frequency) / 10000 +
                "GHz Bandwidth: " +
                grantsToShow[popupBoxGrant].bandwidth / 10 +
                "MHz");
            if (overlapCheck) { printToOutput("Conflict caused by acceptance!"); }
            if (document.querySelector('input[id="pauseOnPopup"]').checked) {
                play();
            }
        }

        // on clicking Deny
        if (x > popupBox.x + 387 &&
            x < popupBox.x + 387 + 183 &&
            y > popupBox.y + 83 &&
            y < popupBox.y + 83 + 183) {
            popupOpened = false;
            console.log("Deny Clicked");
            grantsToShow[popupBoxGrant].acceptStatus = 3;

            var denystr = "Manually denied " + "SU Grant F:";
            var freqstr = (baseFrequency + grantsToShow[popupBoxGrant].frequency) / 10000 + "GHz";
            freqstr = grantsToShow[i].frequencyb > 0 ? "(" + freqstr + ", " + (baseFrequency + grantsToShow[popupBoxGrant].frequencyb) / 10000 + "GHz)" : freqstr;
            freqstr = freqstr + " Bandwidth: " +
                grantsToShow[popupBoxGrant].bandwidth / 10 +
                "MHz";
            denystr += freqstr;
            printToOutput(denystr);
            if (document.querySelector('input[id="pauseOnPopup"]').checked) {
                play();
            }
        }
        if (popupBox.freqText2.length > 0) {
            // on clicking Accept2 
            if (x > popupBox.x + 20 &&
                x < popupBox.x + 20 + 112 &&
                y > popupBox.y + 242 &&
                y < popupBox.y + 242 + 38) {
                popupOpened = false;
                console.log("Accept 2 Clicked");
                var overlapCheck = checkOverlap(grantsToShow[popupBoxGrant].startTime, grantsToShow[popupBoxGrant].startTime + grantsToShow[popupBoxGrant].length, grantsToShow[popupBoxGrant].frequencyb, grantsToShow[popupBoxGrant].bandwidth);
                approvedGrants.push(grantsToShow[popupBoxGrant]);
                grantsToShow[popupBoxGrant].acceptStatus = overlapCheck ? 2 : 1;

                convertGrant(
                    grantsToShow[popupBoxGrant],
                    true,
                    overlapCheck ? "red" : "cyan", // ternary operation for color
                    "SU Grant F: " +
                    (baseFrequency + grantsToShow[popupBoxGrant].frequencyb) / 10000 +
                    "GHz Bandwidth: " +
                    grantsToShow[popupBoxGrant].bandwidth / 10 +
                    "MHz"
                );

                printToOutput("Manually accepted " + "SU Grant F: " +
                    (baseFrequency + grantsToShow[popupBoxGrant].frequency) / 10000 +
                    "GHz Bandwidth: " +
                    grantsToShow[popupBoxGrant].bandwidth / 10 +
                    "MHz");
                if (overlapCheck) { printToOutput("Conflict caused by acceptance!"); }
                if (document.querySelector('input[id="pauseOnPopup"]').checked) {
                    play();
                }
            }

        }


        return; // all other clicks are ignored if popup is open
    }

    // CHECK REQUESTED GRANTS
    grantsToShow.forEach(function (grant, idx) {
        if (grant.acceptStatus !== 0) {
            return; // skip actioned grants, return == continue within forEach()
        }

        if (grant.showTime > myGameArea.frameNo) {
            return; // skip denied grants, return == continue within forEach()
        }

        var startPlace = grant.frequency - grant.bandwidth / 2;
        var startPlaceb = grant.frequencyb - grant.bandwidth / 2;  // freq2 startplace

        startPlace = frequencyToPixelConversion(startPlace);
        startPlaceb = frequencyToPixelConversion(startPlaceb);
        pixHeight = bandwidthToComponentHeight(grant.bandwidth);
        if (
            x > grant.startTime - myGameArea.frameNo &&
            x < grant.startTime - myGameArea.frameNo + grant.length &&
            y > startPlace &&
            y < startPlace + pixHeight
        ) {
            //console.log("clicked grant " + grant.id);
            //console.log("x: " + x + " y: " + y);

            popupBox.title = "Bandwidth: " + grant.bandwidth / 10 + "MHz";

            popupBox.startTime = parseMillisecondsIntoReadableTime(grant.startTime - nowLinePosition, false) + " Start Time";
            popupBox.lenStr = parseMillisecondsIntoReadableTime(grant.length, false) + " Duration";

            popupBox.freqText1 = "Frequency: " + (baseFrequency + grant.frequency) / 10000 + " GHz";
            if (grant.frequencyb > 0) {
                popupBox.freqText2 = "Frequency: " + (baseFrequency + grant.frequencyb) / 10000 + " GHz";
            } else {
                popupBox.freqText2 = "";
            }
            if (document.querySelector('input[id="pauseOnPopup"]').checked) {
                pause();
            }
            popupBoxGrant = idx;
            popupOpened = true;
            updateGameArea();
        }

        if (
            x > grant.startTime - myGameArea.frameNo &&
            x < grant.startTime - myGameArea.frameNo + grant.length &&
            y > startPlaceb &&
            y < startPlaceb + pixHeight
        ) {
            popupBox.title = "Bandwidth: " + grant.bandwidth / 10 + "MHz";

            popupBox.startTime = parseMillisecondsIntoReadableTime(grant.startTime - nowLinePosition, false) + " Start Time";
            popupBox.lenStr = parseMillisecondsIntoReadableTime(grant.length, false) + " Duration";

            popupBox.freqText1 = "Frequency: " + (baseFrequency + grant.frequency) / 10000 + "GHz";
            popupBox.freqText2 = "Frequency: " + (baseFrequency + grant.frequencyb) / 10000 + "GHz";


            if (document.querySelector('input[id="pauseOnPopup"]').checked) {
                pause();
            }
            popupBoxGrant = idx;
            popupOpened = true;
            updateGameArea();
        }
    });
};



function seedChange(value) {
    // clear grants on seed change
    grantsToShow.forEach(function (grant, idx) {
        grant.acceptStatus = 3;
    }
    );
    popupOpened = false; // close popup on seed change
    seedValue = value;

    // ! 0 is being hardcoded to random generation here !
    if (value === 0) {
        document.getElementById("randomFactors").hidden = false;
        startGame(null);
    } else {
        document.getElementById("randomFactors").hidden = true;
        loadSetSeed(seedValue, startGame);
    }

}

/**
 * PU's and Requests are loaded from js/setSeeds.js, unless random generation is requested
 */
function loadGrantsAndPUs() {
    // ! 0 is being hardcoded to random generation here !
    if (setSeed == null && seedValue !== 0) {
        return;
    }
    if (seedValue !== 0) {
        setSeed["PU"].forEach(function (seed) {
            makePUGrant(new Grant(seed.startTime, seed.length, seed.frequency, seed.bandwidth, seed.frequencyb, seed.showTime));
        });

        setSeed["REQ"].forEach(function (seed) {
            grant = new Grant(seed.startTime, seed.length, seed.frequency, seed.bandwidth, seed.frequencyb, seed.showTime);
            grantsToShow.push(grant);
            requestList.push(grant);
        });

    } else {
        // RANDOM GENERATION
        var showTime = 0;
        var startTime = 0;
        var length = 0;
        var frequency = 0;
        var minST = startTime + 50;
        var maxST = startTime + 5000;

        // * Random generation values from user input
        var randNumPUs = document.getElementById("punum").value;
        var randNumREQs = document.getElementById("reqnum").value;
        var maxBandwidth = document.getElementById("maxband").value * 10;
        var minBandwidth = document.getElementById("minband").value * 10;
        var minLength = document.getElementById("minlen").value;
        var maxLength = document.getElementById("maxlen").value;

        //(startTime, length, frequency, bandwidth, frequencyb, showTime)
        var bandwidth = 0;
        for (var i = 0; i < randNumPUs; i++) {
            gStartTime = Math.floor(Math.random() * maxST) + minST;
            length = Math.floor(Math.random() * maxLength) + minLength;
            frequency =
                Math.floor(
                    Math.random() * (baseFrequency + frequencyRange - maxBandwidth / 2)
                ) +
                minBandwidth / 2;
            bandwidth = Math.floor(((Math.random() * maxBandwidth) + minBandwidth) / 50) * 50;
            makePUGrant(new Grant(gStartTime, length, frequency, bandwidth, 0, 0));
        }

        var minDSS = 500; //minimum difference between start time and show time
        var maxDSS = 1000;
        var frequencyb = 0;
        //REQUESTS
        for (var i = 0; i < randNumREQs; i++) {
            gStartTime = Math.floor(Math.random() * maxST) + minST;
            showTime =
                Math.floor(Math.random() * (startTime - minDSS)) + (startTime - maxDSS);
            length = Math.floor(Math.random() * maxLength) + minLength;
            frequency =
                Math.floor(Math.random() * (frequencyRange - maxBandwidth / 2)) +
                minBandwidth / 2;
            if (Math.floor(Math.random() * 2)) {
                frequencyb =
                    Math.floor(Math.random() * (frequencyRange - maxBandwidth / 2)) +
                    minBandwidth / 2;
            } else {
                frequencyb = 0;
            }
            bandwidth = Math.floor(((Math.random() * maxBandwidth) + minBandwidth) / 50) * 50;
            grant = new Grant(
                gStartTime,
                length,
                frequency,
                bandwidth,
                frequencyb,
                showTime
            );
            grantsToShow.push(grant);
            requestList.push(grant);
        }
        printToOutput("   " + approvedGrants.length + " PUs, " + grantsToShow.length + " REQs");
        printToOutput("   |   BW: " + (minBandwidth / 10) + "MHz - " + (maxBandwidth / 10) + "MHz", false);
        printToOutput("   |  LEN: " + minLength + "ms - " + maxLength + "ms", false);
        printToOutput("====================================================================");
    }
}



/**
 * Component object for canvas everything drawn on the canvas is a component
 * object .update() is called to draw the object onto the canvas
 *
 * @param {any} width
 * @param {any} height
 * @param {any} color
 * @param {any} x
 * @param {any} y
 * @param {string} type Either "text", "select", or null
 */
function component(width, height, color, x, y, type = null) {
    this.type = type;
    this.score = 0;
    this.width = width;
    this.height = height;
    this.speedX = 0;
    this.speedY = 0;
    this.x = x;
    this.y = y;
    this.gravity = 0;
    this.gravitySpeed = 0;
    this.update = function () {
        ctx = myGameArea.context;
        switch (this.type) {
            case "text":
                ctx.font = this.width + " " + this.height;
                ctx.fillStyle = color;
                ctx.fillText(this.text, this.x, this.y);
                break;
            case "select": // ! hoverover box, !! TEMP
                ctx.globalAlpha = 0.6; // our next draw is transparent
                ctx.fillStyle = color;
                ctx.fillRect(this.x, this.y, this.width, this.height);
                ctx.globalAlpha = 1; // if not set back to 100% opacity, all draws after this will be transparent
                if (this.text !== undefined) {
                    ctx.fillStyle = "black";
                    ctx.font = 'Bold 36px Arial';
                    ctx.fillText(this.text, this.x, this.y + 36);
                }
                break;
            case "popup": // ! popup box, needs to be cleaned up
                ctx.save(); // save context

                // draw popup box background
                ctx.globalAlpha = 0.80; // our next draw is transparent
                ctx.fillStyle = color;
                ctx.fillRect(this.x, this.y, this.width, this.height);

                // if not set back to 100% opacity, all draws after this will be transparent
                ctx.globalAlpha = 1;

                // * Title
                ctx.font = 'Bold 44px Arial';
                ctx.fillStyle = "black";
                ctx.fillText(this.title, this.x + 5, this.y + 44);

                // * Sub-Title
                ctx.font = '18px Arial';
                ctx.fillStyle = "black";
                ctx.fillText(this.startTime, this.x + 5, this.y + 68);
                ctx.fillText(this.lenStr, this.x + 5, this.y + 88);



                // * Freq 1

                // draw frequency 1 text
                ctx.font = 'Bold 30px Arial';
                ctx.fillStyle = "black";
                ctx.fillText(this.freqText1, this.x + 5, this.y + 125);

                // draw Accept text
                ctx.fillStyle = "green";
                ctx.fillRect(this.x + 20, this.y + 132, 112, 38);
                ctx.fillStyle = "white";
                ctx.font = 'Bold 30px Arial';
                ctx.fillText("Accept", this.x + 25, this.y + 160);

                // * Freq 2

                if (this.freqText2.length > 1) {
                    // draw frequency 2 text
                    ctx.font = 'Bold 30px Arial';
                    ctx.fillStyle = "black";
                    ctx.fillText(this.freqText2, this.x + 5, this.y + 235);

                    // draw Accept2 text
                    ctx.fillStyle = "green";
                    ctx.fillRect(this.x + 20, this.y + 242, 112, 38);
                    ctx.fillStyle = "white";
                    ctx.font = 'Bold 30px Arial';
                    ctx.fillText("Accept", this.x + 25, this.y + 270);
                }

                // * Deny Button
                ctx.fillStyle = "red";
                ctx.globalAlpha = 0.30; // our next draw is transparent
                ctx.fillRect(this.x + 387, this.y + 83, 183, 183);
                ctx.globalAlpha = 1.0; // our next draw is transparent
                ctx.fillStyle = "white";
                ctx.font = 'Bold 50px Arial';
                ctx.fillText("Deny", this.x + 387 + 30, this.y + 83 + 106);

                // * [x] button
                ctx.fillStyle = "red";
                ctx.fillRect(this.x + 575, this.y, 25, 25);
                ctx.fillStyle = "white";
                ctx.font = 'Bold 28px Arial';
                ctx.fillText("x", this.x + this.width - 20, this.y + 20);
                ctx.restore(); // restore prior context

                break;
            default:
                // anything else, such as the rects representing the grant
                ctx.fillStyle = color;
                ctx.fillRect(this.x, this.y, this.width, this.height);
        }
    };
}

function makeSUGrant(grant) {
    convertGrant(grant, false, "cyan", "SU Grant F: " + (baseFrequency + grant.frequency) / 10000 + "GHz Bw: " + grant.bandwidth / 10 + "MHz");
    approvedGrants.push(grant);
}

function makePUGrant(grant) {
    convertGrant(grant, false, "green", "PU Grant F: " + (baseFrequency + grant.frequency) / 10000 + "GHz Bw: " + grant.bandwidth / 10 + "MHz");
    approvedGrants.push(grant);
}

function createFrequencyTexts() {
    var numberOfTexts = 10;

    var frequencyDifference = frequencyRange / numberOfTexts;
    var startPlace = 0;
    for (i = 0; i <= numberOfTexts; i += 1) {
        startPlace = frequencyToPixelConversion(i * frequencyDifference);
        var text = new component("15px", "Consolas", "black", 10, startPlace, "text");
        text.text = ((baseFrequency + (i * frequencyDifference)) / 10000).toPrecision(4) + "GHz-";
        frequencyTexts.push(text);
    }
}


function updateGameArea() {
    var x, height, gap, minHeight, maxHeight, minGap, maxGap;

    myGameArea.clear();
    myGameArea.frameNo += 1;


    for (i = 0; i < grantsToShow.length; i += 1) {
        if (grantsToShow[i].showTime == myGameArea.frameNo) { // ! if showTime is too low (0), the equality causes it to never show up
            var startFrequency = grantsToShow[i].frequency - grantsToShow[i].bandwidth / 2; // calc start frequency
            var startPlace = frequencyToPixelConversion(startFrequency); // convert startFrequency to pixel coordinates
            var heightOfBlock = bandwidthToComponentHeight(grantsToShow[i].bandwidth); // calc height of block

            // create the grant component
            var queuingGrant = new component(
                grantsToShow[i].length,
                heightOfBlock,
                "pink",
                grantsToShow[i].startTime - myGameArea.frameNo,
                startPlace,
                "select"
            );
            queuingGrant.grant = grantsToShow[i];


            queuedGrantRects.push(queuingGrant); // push onto mygrants

            // if multiple freqs
            if (grantsToShow[i].frequencyb > 0) {
                var startFrequencyb = grantsToShow[i].frequencyb - grantsToShow[i].bandwidth / 2; // calc start frequency
                var startPlaceb = frequencyToPixelConversion(startFrequencyb); // convert startFrequency to pixel coordinates
                queuingGrant = new component(
                    grantsToShow[i].length,
                    heightOfBlock,
                    "pink",
                    grantsToShow[i].startTime - myGameArea.frameNo,
                    startPlaceb,
                    "select"
                );
                queuingGrant.grant = grantsToShow[i];
                queuedGrantRects.push(queuingGrant); // push onto mygrants
            }
        }
    }

    for (i = 0; i < myGrants.length; i += 1) {
        myGrants[i].x += -1;
        myGrants[i].update();
    }


    for (i = 0; i < queuedGrantRects.length; i += 1) {
        // if grant is not accepted nor denied yet  
        if (queuedGrantRects[i].grant.acceptStatus === 0) {
            queuedGrantRects[i].x += -1;
            if (queuedGrantRects[i].grant.showTime <= myGameArea.frameNo) {
                queuedGrantRects[i].update();

            }
        }
    }

    tempGrantComponent.x += -1;

    myTime.text = "Now Time: " + parseMillisecondsIntoReadableTime(myGameArea.frameNo);
    grantSummaryText.text = ""/*"Grants Approved: " + approvedGrantCount + " " +
    "Grants Denied: " + deniedGrantCount + " " +
    "Grants Moved: " + movedGrantCount + " " + 
    "Grants Missed: " + cancelledGrantCount;*/
    grantSummaryBox.update();
    grantSummaryText.update();
    myTime.update();
    nowLine.update();

    tempGrantComponent.update();
    for (i = 0; i < movingTexts.length; i += 1) {
        movingTexts[i].x += -1;
        movingTexts[i].update();
    }

    // draw hovered grant right before bandwidthBox
    for (i = 0; i < hoveredGrant.length; i += 1) {
        hoveredGrant[i].x += -1;
        hoveredGrant[i].update();
    }

    bandwidthBox.update();

    for (i = 0; i < frequencyTexts.length; i += 1) {
        frequencyTexts[i].update();
    }
    if (myGameArea.frameNo >= stopTime) {
        clearInterval(myGameArea.interval);
    }

    // This is last, to draw over all other components
    if (popupOpened) {
        popupBox.update();
    }

}


function everyinterval(n) {
    if ((myGameArea.frameNo / n) % 1 == 0) { return true; }
    return false;
}


function parseMillisecondsIntoReadableTime(minutes) {

    var days = minutes / (60 * 24);
    var d = Math.floor(days);
    //Get hours from milliseconds
    var hours = (days - d) * 24;
    var absoluteHours = Math.floor(hours);
    var h = absoluteHours > 9 ? absoluteHours : '0' + absoluteHours;

    //Get remainder from hours and convert to minutes
    var minutes = (hours - absoluteHours) * 60;
    var absoluteMinutes = Math.floor(minutes);
    var m = absoluteMinutes > 9 ? absoluteMinutes : '0' + absoluteMinutes;

    //Get remainder from minutes and convert to seconds
    var seconds = (minutes - absoluteMinutes) * 60;
    var absoluteSeconds = Math.floor(seconds);
    var s = absoluteSeconds > 9 ? absoluteSeconds : '0' + absoluteSeconds;


    return d + 'd:' + h + 'h:' + m + 'm ' + myGameArea.speed;
}

function checkOverlap(startTime, endTime, frequency, bandwidth) {
    for (i = 0; i < approvedGrants.length; i += 1) {
        if (approvedGrants[i].startTime <= startTime && (approvedGrants[i].startTime + approvedGrants[i].length) >= startTime) {
            if (checkFrequency(approvedGrants[i].frequency, approvedGrants[i].bandwidth, frequency, bandwidth)) {
                return true;
            }
        } else if ((startTime <= approvedGrants[i].startTime) && (endTime >= (approvedGrants[i].startTime + approvedGrants[i].length))) {
            if (checkFrequency(approvedGrants[i].frequency, approvedGrants[i].bandwidth, frequency, bandwidth)) {
                return true;
            }
        } else if ((approvedGrants[i].startTime >= startTime) && (approvedGrants[i].startTime <= endTime)) {
            if (checkFrequency(approvedGrants[i].frequency, approvedGrants[i].bandwidth, frequency, bandwidth)) {
                return true;
            }
        } else if ((approvedGrants[i].startTime <= startTime) && ((approvedGrants[i].startTime + approvedGrants[i].length) >= endTime)) {
            if (checkFrequency(approvedGrants[i].frequency, approvedGrants[i].bandwidth, frequency, bandwidth)) {
                return true;
            }
        }
    }
    return false;
}

function checkFrequency(freqa, banda, freqb, bandb) {
    var la = freqa - (banda / 2);
    var ha = freqa + (banda / 2);
    var lb = freqb - (bandb / 2);
    var hb = freqb + (bandb / 2);

    if ((lb <= la && hb >= la) || (la <= lb && ha >= hb) || (lb <= ha && hb >= ha) || (lb <= la && hb >= ha)) {
        return true;
    }
    else {
        return false;
    }
}

function frequencyToPixelConversion(frequency) {
    var visibleScreenPixelCount = canvasHeight - titleOffset - summaryTextHeight;
    var percentage = frequency / frequencyRange;
    return (visibleScreenPixelCount * percentage) + titleOffset;
}

function bandwidthToComponentHeight(bandwidth) {
    var visibleScreenPixelCount = canvasHeight - titleOffset - summaryTextHeight;
    var percentage = bandwidth / frequencyRange;
    return visibleScreenPixelCount * percentage;
}



//grant, true/false/ colorstring
function convertGrant(grant, b, color, text) {
    //width, height, color, x, y



    if (b) {
        //use frequency b
        var startFrequency = grant.frequencyb - (grant.bandwidth / 2);
        var startPlace = frequencyToPixelConversion(startFrequency);
        var heightOfBlock = bandwidthToComponentHeight(grant.bandwidth);

        var approvedGrant = new component(grant.length, heightOfBlock, color, grant.startTime - myGameArea.frameNo, startPlace);
        myGrants.push(approvedGrant);

        grantText = new component("20px", "Consolas", "black", grant.startTime - myGameArea.frameNo, startPlace + heightOfBlock / 2, "text");
        grantText.text = text;
        movingTexts.push(grantText);

    }
    else {
        //use frequency a
        var startFrequency = grant.frequency - (grant.bandwidth / 2);
        var startPlace = frequencyToPixelConversion(startFrequency);
        var heightOfBlock = bandwidthToComponentHeight(grant.bandwidth);

        var approvedGrant = new component(grant.length, heightOfBlock, color, grant.startTime - myGameArea.frameNo, startPlace);
        myGrants.push(approvedGrant);

        grantText = new component("20px", "Consolas", "black", grant.startTime - myGameArea.frameNo, startPlace + heightOfBlock / 2, "text");
        grantText.text = text;
        movingTexts.push(grantText);
    }
}

function moveGrant(grant) {
    movedGrantCount++;
}

function cancelGrant(grant) {
    cancelledGrantCount++;
}

function pause() {
    isPaused = true;
    clearInterval(myGameArea.interval);
}

function play() {
    isPaused = false;
    myGameArea.speed = "1x";
    clearInterval(myGameArea.interval);
    myGameArea.interval = setInterval(updateGameArea, 20);
}

function setFrameInterval(speed) {
    myGameArea.speed = 1 / (speed) + 'x';
    clearInterval(myGameArea.interval);
    myGameArea.interval = setInterval(updateGameArea, speed * 20);

}

function restart() {
    location.reload();
}

function runCode() {
    // split user code by line
    var userCode = editor.getValue().split("\n");
    // first and last lines are readonly and set by us, ignore them
    userCode[0] = "";
    userCode[userCode.length - 1] = "";
    // join string back
    userCode = userCode.join("\n");


    eval(userCode);
    for (var i = 0; i < finalGrantList.length; i++) {
        makeSUGrant(finalGrantList[i]);
        requestList.splice(requestList.indexOf(finalGrantList[i]), 1);
        var addingOverlapped = checkOverlap(finalGrantList[i].startTime, finalGrantList[i].endTime, finalGrantList[i].frequency, finalGrantList[i].bandwidth);
        if (addingOverlapped) {
            finalGrantList[i].acceptStatus = 2;
        } else {
            finalGrantList[i].acceptStatus = 1;
        }
    }
    finalGrantList = []


}

