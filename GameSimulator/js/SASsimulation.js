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
    theme: "duotone-dark",
    resize: "vertical",
    mode: { name: "javascript", globalVars: true }
}
);

// ! codemirror
var displayConsole = CodeMirror.fromTextArea(
    document.getElementById("consoleOutput"), {
    styleActiveLine: false,
    matchBrackets: false,
    lineNumbers: false,
    scrollbarStyle: "overlay",
    readOnly: "nocursor",
    theme: "duotone-light",
    resize: "vertical",
    mode: { name: "javascript", globalVars: true }
}
);


// resize 
editor.setSize(1000, 200);
displayConsole.setSize(500, 100);


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



function printToOutput(str) {
    var con = document.getElementById("consoleOutput");
    con.innerHTML = con.innerHTML + "\n" + str;
}

function clearConsole() {
    var con = document.getElementById("consoleOutput");
    con.innerHTML = ""
}



function startGame(readSeed) {
    setSeed = readSeed;
    nowLine = new component(2, canvasHeight - summaryTextHeight - titleOffset, "red", nowLinePosition, 50);
    grantSummaryText = new component("20px", "Consolas", "black", 150, canvasHeight - 50, "text");
    grantSummaryBox = new component(canvasWidth, summaryTextHeight, "white", 0, canvasHeight - summaryTextHeight);
    bandwidthBox = new component(100, canvasHeight, "white", 0, 0);

    myGrants = [];
    approvedGrants = [];
    movingTexts = [];
    frequencyTexts = [];
    grantsToShow = [];
    isPaused = false;


    myTime = new component("30px", "Consolas", "black", nowLinePosition, 40, "text");




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

function seedChange(value) {
    // clear grants on seed change
  grantsToShow.forEach(function (grant, idx) {
    grant.acceptStatus = 3;
  }
  );
  popupOpened = false; // close popup on seed change
  seedValue = value;

    seedValue = value;
      // ! 0 is being hardcoded to random generation here !
  value === 0 ? startGame(null) : loadSetSeed(seedValue, startGame);

}

function loadGrantsAndPUs() {
    setSeed["PU"].forEach(function (seed) {
        makePUGrant(new Grant(seed.startTime, seed.length, seed.frequency, seed.bandwidth, seed.frequencyb, seed.showTime));
    });

    setSeed["REQ"].forEach(function (seed) {
        grant = new Grant(seed.startTime, seed.length, seed.frequency, seed.bandwidth, seed.frequencyb, seed.showTime);
        requestList.push(grant);
    });

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

    for (i = 0; i < myGrants.length; i += 1) {
        myGrants[i].x += -1;
        myGrants[i].update();
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

    bandwidthBox.update();

    for (i = 0; i < frequencyTexts.length; i += 1) {
        frequencyTexts[i].update();
    }
    if (myGameArea.frameNo >= stopTime) {
        clearInterval(myGameArea.interval);
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
    var string = editor.getValue();
    string.replaceAll("rm", "");
    eval(string);
    for (var i = 0; i < finalGrantList.length; i++) {
        makeSUGrant(finalGrantList[i]);
    }

    displayConsole.setValue(document.getElementById('consoleOutput').value);
}

