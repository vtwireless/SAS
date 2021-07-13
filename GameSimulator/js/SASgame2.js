// SASgame2.js - vue implementation
/* jshint esversion: 6 */

var canvasWidth = 1200;
var canvasHeight = 700;

var approvedGrantCount = 0;
var deniedGrantCount = 0;
var missedGrantCount = 0;
var conflictingGrantCount = 0;

var grantSummaryText;
var grantSummaryBox;
var bandwidthBox;

var summaryTextHeight = 100;
var frequencyRange = 1500; //35000-37000
var titleOffset = 50;
var baseFrequency = 35500;
var nowLinePosition = 200;

var seedValue = 1;
var isPaused = false;
var score = 0;
var outOf = 0;


/**
 * Component object for canvas everything drawn on the canvas is a component
 * object .update() is called to draw the object onto the canvas
 *
 * @param {any} width
 * @param {any} height
 * @param {any} color
 * @param {any} x
 * @param {any} y
 * @param {string} type Either "text", "transparentRect", or "rect"
 * @param {string} text [Optional], overlays text on rects
 */
function component(width, height, color, x, y, type = null, text = "") {
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
            case "transparentRect": // ! hoverover box, !! TEMP
                ctx.globalAlpha = 0.4; // our next draw is at 40% opacity
                ctx.fillStyle = color;
                ctx.fillRect(this.x, this.y, this.width, this.height);
                ctx.globalAlpha = 1; // if not set back to 100% opacity, all draws after this will be transparent
                break;
            case "rect":
            default:
                // anything else, such as the rects representing the grant
                ctx.fillStyle = color;
                ctx.fillRect(this.x, this.y, this.width, this.height);
        }
    };
}

function frequencyToPixelConversion(frequency) {
    var visibleScreenPixelCount = canvasHeight - titleOffset - summaryTextHeight;
    var percentage = frequency / frequencyRange;
    return visibleScreenPixelCount * percentage + titleOffset;
}

function bandwidthToComponentHeight(bandwidth) {
    var visibleScreenPixelCount = canvasHeight - titleOffset - summaryTextHeight;
    var percentage = bandwidth / frequencyRange;
    return visibleScreenPixelCount * percentage;
}


class Grant {
    constructor(startTime, length, frequency, bandwidth, frequencyb, showTime) {
        this.startTime = startTime;
        this.length = length;
        this.frequency = frequency;
        this.bandwidth = bandwidth;
        this.frequencyb = frequencyb;
        this.showTime = showTime;
        var heightOfBlock = bandwidthToComponentHeight(bandwidth);

        var startFrequency = frequency - bandwidth / 2;
        var startPlace = frequencyToPixelConversion(startFrequency);
        this.component1 = new component(
            length,
            heightOfBlock,
            "green",
            startTime - myGameArea.frameNo,
            startPlace,
            "rect"
        );

        if (this.frequencyb > 0) {
            var startFrequencyb = frequencyb - bandwidth / 2;
            var startPlaceb = frequencyToPixelConversion(startFrequencyb);
            this.component2 = new component(
                length,
                heightOfBlock,
                "green",
                startTime - myGameArea.frameNo,
                startPlaceb,
                "rect"
            );
        } else {
            this.component2 = null;
        }
    }
}

/** The canvas itself */
var myGameArea = {
    canvas: document.getElementById("grantCanvas"),
    speed: "1x",
    frameNo: 0,
    start: function () {
        if (this.interval) {
            clearInterval(this.interval);
        }
        this.context = this.canvas.getContext("2d");

        this.isPaused = false;
        this.interval = setInterval(updateGameArea, 20);
    },
    clear: function () {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    },
};

var app = new Vue({
    el: '#ui',
    data: {
        puGrants: [],
        requests: []

    },
    methods: {

    },
    computed: {

    },
});


app.puGrants.push(new Grant(1, 500, 350, 200, 355, 0));
app.puGrants.push(new Grant(1000, 500, 350, 200, 355, 0));
app.puGrants.push(new Grant(1500, 500, 450, 100, 255, 0));
app.puGrants.push(new Grant(1200, 1000, 600, 200, 355, 0));
app.puGrants.push(new Grant(1300, 300, 850, 150, 355, 0));
app.puGrants.push(new Grant(1600, 1500, 700, 400, 355, 0));

app.requests.push(new Grant(1000, 500, 1350, 100, 355, 0));
app.requests.push(new Grant(2000, 500, 450, 200, 505, 0));
app.requests.push(new Grant(1300, 200, 1370, 200, 0, 200));
app.requests.push(new Grant(1300, 200, 570, 200, 0, 1000));
app.requests.push(new Grant(1400, 300, 1400, 200, 0, 1000));
app.requests.push(new Grant(1400, 200, 800, 200, 0, 1000));
app.requests.push(new Grant(2300, 600, 1470, 200, 0, 1800));
app.requests.push(new Grant(2300, 1200, 1470, 200, 1250, 1600));
app.requests.push(new Grant(2400, 200, 1200, 200, 1750, 1900));
app.requests.push(new Grant(2400, 200, 1400, 200, 0, 1900));


