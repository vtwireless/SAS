// SASgame.js - canvas scripting for SASgame.html
/* jshint esversion: 6 */

// * Canvas drawloop is initialized onload by SASgame.html:19 '<body onload="startGame()">'

// !---------------------- global variable init  -----------------------------!

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
 * Maximum total runtime in ticks(iterations of draw loop)
 *
 * @type {int}
 */
var stopTime = 5000;

/**
 * Text component holding current 'time' based off tickrate
 *
 * @type {component}
 */
var myTime;
/**
 * Rect component representing current time line indicator
 *
 * @type {component}
 */
var nowLine;
/**
 * Text component representing highlighted grant on mouseover
 *
 * @type {component}
 */
var currHover;
/**
 * Rect representing highlighted grant on mouseover
 *
 * @type {component}
 */
var hoveredGrant;


/**
 * COMPONENT RECTS OF THE GRANTS TO DRAW
 *
 * @type {component[]}
 */
var myGrants = [];
/**
 * GRANTS OF THE GRANTS TO DRAW, SAME IDX AS myGrants
 *
 * @type {Grant[]}
 */
var approvedGrants = [];

/**
 * Similar to frequencyTexts, an array of text components being drawn over rect
 * components in the canvas
 *
 * @type {component[]}
 */
var movingTexts = [];

/**
 * Similar to movingTexts, an array of text components being drawn over rect
 * components in the canvas
 *
 * @type {component[]}
 */
var frequencyTexts = [];

/**
 * Array of rect components representing the initial hardcoded (or randomly
 * generated) grants
 *
 * @type {component[]}
 */
var grantsToShow = [];


/**
 * Array of rect components representing the requested grants
 * pre-selection
 *
 * @type {component[]}
 */
var queuedGrantRects = [];

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
popupBox.title = "";
popupBox.freqText1 = "";
popupBox.freqText2 = "";

var popupOpened = false;


/** The canvas itself */
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
    document.body.insertBefore(this.canvas, document.body.childNodes[4]);
    this.frameNo = 0;
    loadGrantsAndPUs();

    createFrequencyTexts();
    this.isPaused = false;
    this.interval = setInterval(updateGameArea, 20);
  },
  clear: function () {
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
  },
};

// !---------------------- TEMP: canvas event listeners  -----------------------------!


myGameArea.canvas.onmousemove = function (e) {
  var rect = this.getBoundingClientRect(),
    x = e.clientX - rect.left,
    y = e.clientY - rect.top,
    i = 0,
    r;

  // Dont do anything if popup box is open
  if (popupOpened) {
    return; // all other clicks are ignored if popup is open
  }
  var grantHovered = false;

  queuedGrantRects.forEach(function (r) {
    if (grantHovered) {
      return;
    }
    if (x >= r.x && x <= r.x + r.width && y >= r.y && y <= r.y + r.height) {
      hoveredGrant.x = r.x;
      hoveredGrant.y = r.y;
      hoveredGrant.width = r.width;
      hoveredGrant.height = r.height;
      hoveredGrant.text = r.text;
      hoveredGrant.id = r.id;
      hoveredGrant.type = r.type;
      hoveredGrant.color = "red";
      grantHovered = true;
      return;
    }
  });

  if (!grantHovered) {
    hoveredGrant.x = 0;
    hoveredGrant.y = 0;
    hoveredGrant.width = 0;
    hoveredGrant.height = 0;
    
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
    if (x > popupBox.x + popupBox.width - 60 &&
      x < popupBox.x + popupBox.width &&
      y > popupBox.y &&
      y < popupBox.y + 40) {
      popupOpened = false;
      play();
    }
    return; // all other clicks are ignored if popup is open
  }

  // CHECK REQUESTED GRANTS
  grantsToShow.forEach(function (grant, idx) {
    if (grant.denied) {
      return; // skip denied grants, return == continue within forEach()
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
      popupBox.freqText1 = "Frequency: " + (baseFrequency + grant.frequency) / 10000 + " GHz";
      if (grant.frequencyb > 0) {
        popupBox.freqText2 = "Frequency: " + (baseFrequency + grant.frequencyb) / 10000 + " GHz";
      } else {
        popupBox.freqText2 = "";
      }
      pause();
      popupOpened = true;
      updateGameArea();
    }

    if (
      x > grant.startTime - myGameArea.frameNo &&
      x < grant.startTime - myGameArea.frameNo + grant.length &&
      y > startPlaceb &&
      y < startPlaceb + pixHeight
    ) {
      popupBox.title = "Bandwidth: " +
        grant.bandwidth / 10 + "MHz";
      popupBox.freqText1 = "Frequency: " + (baseFrequency + grant.frequencyb) / 10000 + "GHz";
      popupBox.freqText2 = "Frequency: " + (baseFrequency + grant.frequency) / 10000 + "GHz";

      pause();
      popupOpened = true;
      updateGameArea();
    }
  });
};


// !---------------------- classes and functions  -----------------------------!

class Grant {
  constructor(startTime, length, frequency, bandwidth, frequencyb, showTime) {
    this.startTime = startTime;
    this.length = length;
    this.frequency = frequency;
    this.bandwidth = bandwidth;
    this.frequencyb = frequencyb;
    this.showTime = showTime > 0 ? showTime : 1; // if showtime is 0, grants may never be queued
    this.denied = false;
  }
}

/** Inits components and arrays for drawing to canvas */
function startGame() {
  nowLine = new component(
    2,
    canvasHeight - summaryTextHeight - titleOffset,
    "red",
    nowLinePosition,
    50
  );
  grantSummaryText = new component(
    "20px",
    "Consolas",
    "black",
    150,
    canvasHeight - 50,
    "text"
  );
  grantSummaryBox = new component(
    canvasWidth,
    summaryTextHeight,
    "white",
    0,
    canvasHeight - summaryTextHeight
  );
  bandwidthBox = new component(100, canvasHeight, "white", 0, 0);
  hoveredGrant = new component(0, 0, "rgba(0, 255, 255)", 0, 0, "select");

  myGrants = [];
  approvedGrants = [];
  movingTexts = [];
  frequencyTexts = [];
  grantsToShow = [];
  isPaused = false;

  myTime = new component(
    "30px",
    "Consolas",
    "black",
    nowLinePosition,
    40,
    "text"
  );
  currHover = new component(
    "30px",
    "Consolas",
    "black",
    nowLinePosition,
    70,
    "text"
  );
  currHover.text = "";
  movingTexts.push(currHover);
  var grantCont = document.getElementById("grantList");
  while (grantCont.firstChild) {
    grantCont.removeChild(grantCont.firstChild);
  }

  myGameArea.start(); // ! Starts the drawloop !
}

function seedChange(value) {
  seedValue = value;
  startGame();
}

/**
 * PU's and grant requests are loaded here PU's (the existing boxes) have
 * makePUGrant() called on them grant requests (the new boxes) are added to
 * grantsToShow seed values of 1 and 2 are hardcoded any other seed value will
 * init random generation
 */
function loadGrantsAndPUs() {
  var grant = new Grant(100, 1000, 100, 200, 0, 0);
  if (seedValue == 1) {
    //PUS
    //(startTime, length, frequency, bandwidth, frequencyb, showTime)
    //grant = new Grant(1, 500, 350, 200, 355, 0);
    makePUGrant(new Grant(1, 500, 350, 200, 355, 0));
    makePUGrant(new Grant(1000, 500, 350, 200, 355, 0));
    makePUGrant(new Grant(1500, 500, 450, 100, 255, 0));
    makePUGrant(new Grant(1200, 1000, 600, 200, 355, 0));
    makePUGrant(new Grant(1300, 300, 850, 150, 355, 0));
    makePUGrant(new Grant(1600, 1500, 700, 400, 355, 0));

    //Requests

    grant = new Grant(1000, 500, 1350, 100, 355, 0);
    grantsToShow.push(grant);
    grant = new Grant(2000, 500, 450, 200, 505, 0);
    grantsToShow.push(grant);
    grant = new Grant(1300, 200, 1370, 200, 0, 200);
    grantsToShow.push(grant);
    grant = new Grant(1300, 200, 570, 200, 0, 1000);
    grantsToShow.push(grant);
    grant = new Grant(1400, 300, 1400, 200, 0, 1000);
    grantsToShow.push(grant);
    grant = new Grant(1400, 200, 800, 200, 0, 1000);
    grantsToShow.push(grant);
    grant = new Grant(2300, 600, 1470, 200, 0, 1800);
    grantsToShow.push(grant);
    grant = new Grant(2300, 1200, 1470, 200, 1250, 1600);
    grantsToShow.push(grant);
    grant = new Grant(2400, 200, 1200, 200, 1750, 1900);
    grantsToShow.push(grant);
    grant = new Grant(2400, 200, 1400, 200, 0, 1900);
    grantsToShow.push(grant);
  } else if (seedValue == 2) {
    //PUS
    makePUGrant(new Grant(1, 500, 30, 1000, 355, 0));
    makePUGrant(new Grant(200, 500, 1350, 200, 355, 0));
    makePUGrant(new Grant(600, 500, 1340, 300, 355, 0));
    makePUGrant(new Grant(1200, 1000, 1350, 200, 355, 0));
    makePUGrant(new Grant(1300, 1350, 200, 150, 355, 0));
    makePUGrant(new Grant(1800, 1700, 1250, 400, 355, 0));
    makePUGrant(new Grant(2200, 1000, 2350, 200, 355, 0));
    makePUGrant(new Grant(2300, 1350, 200, 150, 355, 0));
    makePUGrant(new Grant(2800, 1700, 1250, 400, 355, 0));

    //Requests
    grant = new Grant(1000, 500, 350, 100, 355, 0);
    grantsToShow.push(grant);
    grant = new Grant(2000, 1500, 450, 200, 1505, 1600);
    grantsToShow.push(grant);
    grant = new Grant(1300, 400, 1370, 200, 0, 900);
    grantsToShow.push(grant);
    grant = new Grant(1300, 600, 1370, 200, 0, 800);
    grantsToShow.push(grant);
    grant = new Grant(1400, 700, 700, 200, 0, 1100);
    grantsToShow.push(grant);
    grant = new Grant(1400, 200, 1200, 200, 0, 1100);
    grantsToShow.push(grant);
    grant = new Grant(1000, 500, 1350, 100, 355, 900);
    grantsToShow.push(grant);
    grant = new Grant(2000, 1500, 1350, 200, 1505, 1800);
    grantsToShow.push(grant);
    grant = new Grant(2300, 400, 570, 200, 0, 1900);
    grantsToShow.push(grant);
    grant = new Grant(2300, 1200, 570, 200, 0, 1800);
    grantsToShow.push(grant);
    grant = new Grant(2400, 300, 1300, 200, 0, 2000);
    grantsToShow.push(grant);
    grant = new Grant(2400, 200, 1400, 200, 0, 2000);
    grantsToShow.push(grant);
  } else {
    //RANDOM
    var maxBandwidth = 500;
    var minBandwidth = 150;
    var minLength = 100;
    var maxLength = 2000;
    var showTime = 0;
    var startTime = 0;
    var length = 0;
    var frequency = 0;
    var minST = 100;
    var maxST = startTime;

    //(startTime, length, frequency, bandwidth, frequencyb, showTime)
    var bandwidth = 0;
    for (var i = 0; i < 50; i++) {
      gStartTime = Math.floor(Math.random() * maxST) + minST;
      length = Math.floor(Math.random() * maxLength) + minLength;
      frequency =
        Math.floor(
          Math.random() * (baseFrequency + frequencyRange - maxBandwidth / 2)
        ) +
        minBandwidth / 2;
      bandwidth = Math.floor(Math.random() * maxBandwidth) + minBandwidth;
      makePUGrant((gStartTime, length, frequency, bandwidth, 0, 0));
    }

    maxLength = 1200; //requests
    minBandwidth = 20;
    maxBandwidth = 250;
    var minDSS = 500; //minimum difference between start time and show time
    var maxDSS = 1000;
    var frequencyb = 0;
    //REQUESTS
    for (var i = 0; i < 50; i++) {
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
      bandwidth = Math.floor(Math.random() * maxBandwidth) + minBandwidth;
      bandwidth = Math.ceil(bandwidth / 5) * 5; //round to nearest 5
      grant = new Grant(
        gStartTime,
        length,
        frequency,
        bandwidth,
        frequencyb,
        showTime
      );
      grantsToShow.push(grant);
    }
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
        ctx.globalAlpha = 0.4; // our next draw is at 40% opacity
        ctx.fillStyle = color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.globalAlpha = 1; // if not set back to 100% opacity, all draws after this will be transparent
        break;
      case "popup": // ! popup box, !! TEMP
        ctx.save(); // save context

        // draw popup box background
        ctx.globalAlpha = 0.95; // our next draw is transparent
        ctx.fillStyle = color;
        ctx.fillRect(this.x, this.y, this.width, this.height);

        // if not set back to 100% opacity, all draws after this will be transparent
        ctx.globalAlpha = 1;

        // draw popup box title
        ctx.font = 'Bold 44px Arial';
        ctx.fillStyle = "black";
        ctx.fillText(this.title, this.x + 5, this.y + 44);

        // draw frequency 1 text
        ctx.font = 'Bold 30px Arial';
        ctx.fillStyle = "black";
        ctx.fillText(this.freqText1, this.x + 115, this.y + 125);

        // draw Accept text
        ctx.fillStyle = "lime";
        ctx.font = 'Bold 30px Arial';
        ctx.fillText("Accept", this.x + 125, this.y + 160);

        // draw Deny text 
        ctx.fillStyle = "red";
        ctx.font = 'Bold 30px Arial';
        ctx.fillText("Deny", this.x + 370, this.y + 160);

        if (this.freqText2.length > 1) {
          // draw frequency 2 text
          ctx.font = 'Bold 30px Arial';
          ctx.fillStyle = "black";
          ctx.fillText(this.freqText2, this.x + 115, this.y + 235);

          // draw Accept2 text
          ctx.fillStyle = "lime";
          ctx.font = 'Bold 30px Arial';
          ctx.fillText("Accept", this.x + 125, this.y + 270);

          // draw Deny2 text 
          ctx.fillStyle = "red";
          ctx.font = 'Bold 30px Arial';
          ctx.fillText("Deny", this.x + 370, this.y + 270);

        }

        // x button
        ctx.fillStyle = "black";
        ctx.font = 'Bold 48px Arial';
        ctx.fillText("[x]", this.x + this.width - 60, this.y + 40);
        ctx.restore(); // restore prior context

        break;
      default:
        // anything else, such as the rects representing the grant
        ctx.fillStyle = color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
  };
}

/** Computes actual frequency of a grant and appends units ('Ghz') */
function createFrequencyTexts() {
  var numberOfTexts = 10;

  var frequencyDifference = frequencyRange / numberOfTexts;
  var startPlace = 0;
  for (i = 0; i <= numberOfTexts; i += 1) {
    startPlace = frequencyToPixelConversion(i * frequencyDifference);
    var text = new component(
      "15px",
      "Consolas",
      "black",
      10,
      startPlace,
      "text"
    );
    text.text =
      ((baseFrequency + i * frequencyDifference) / 10000).toPrecision(4) +
      "GHz-";
    frequencyTexts.push(text);
  }
}

/** Canvas draw loop */
function updateGameArea() {
  var x, height, gap, minHeight, maxHeight, minGap, maxGap;


  myGameArea.clear(); // clears canvas to draw a new frame
  myGameArea.frameNo += 1; // increment frame number

  // Iterate through all the requested grants,
  // check whether the current gameTime is within the grant's time window,
  // in which case pass it to queueGrant
  for (i = 0; i < grantsToShow.length; i += 1) {
    if (grantsToShow[i].showTime == myGameArea.frameNo) { // ! if showTime is too low (0), the equality causes it to never show up
      queueGrant(grantsToShow[i]);
    }
  }


  // iterate through all PU grants, increment their x position (tickrate == horizontal speed)
  for (i = 0; i < myGrants.length; i += 1) {
    myGrants[i].x += -1;
    myGrants[i].update();
  }

  for (i = 0; i < queuedGrantRects.length; i += 1) {
    if (!queuedGrantRects[i].grant.denied) {
      queuedGrantRects[i].x += -1;
      if (queuedGrantRects[i].grant.showTime <= myGameArea.frameNo) {
        queuedGrantRects[i].update();

      }
    }
  }


  // calculate score
  score = approvedGrantCount + deniedGrantCount;
  outOf =
    approvedGrantCount +
    deniedGrantCount +
    conflictingGrantCount +
    missedGrantCount;

  // draw current gameTime at the top left corner
  myTime.text =
    "Now Time: " + parseMillisecondsIntoReadableTime(myGameArea.frameNo, true);

  // ! redundant and TEMP ! sets x position of hover text to the current time marker
  currHover.x = nowLinePosition;

  // draws text at bottom of canvas
  grantSummaryText.text =
    "Grants Approved: " +
    approvedGrantCount +
    " " +
    "Grants Denied: " +
    deniedGrantCount +
    " " +
    "Conflicting Grants: " +
    conflictingGrantCount +
    " " +
    "Grants Missed: " +
    missedGrantCount +
    " | SCORE: " +
    score +
    "/" +
    outOf;

  purgeGrantList(); // purge grantDivs not visible in current frame

  grantSummaryBox.update(); // draws summary box
  grantSummaryText.update(); // draws summary text
  currHover.update(); // draws hover text
  myTime.update(); // draws time text
  nowLine.update(); // draws line at current time


  // iterates through component objects (text),
  // increments their position with tickrate, and draws them
  for (i = 0; i < movingTexts.length; i += 1) {
    movingTexts[i].x += -1;
    movingTexts[i].update();
  }

  // ! TEMP ! increments x position of the mouseovered grantDiv
  hoveredGrant.x += -1;
  hoveredGrant.update(); // draw hovered grant

  bandwidthBox.update(); // draws bandwidth box

  // ??
  for (i = 0; i < frequencyTexts.length; i += 1) {
    frequencyTexts[i].update();
  }

  // kills the draw loop when curr tick is above stopTime
  if (myGameArea.frameNo >= stopTime) {
    clearInterval(myGameArea.interval);
  }
  // This is last, to draw over all other components
  if (popupOpened) {
    popupBox.update();
  }
}

/** Iterates through all visible grantDivs and removes ones which have left display context */
function purgeGrantList() {
  var container = document.getElementById("grantList"); // grantList is the side panel with buttons and grants to approve
  // iterate through all the grant 'boxes' in the panel
  for (var i = 0; i < container.childNodes.length; i++) {
    if (container.childNodes[i].id.split('.')[0] < myGameArea.frameNo + 20) {
      //20 is a threshold

      // delete the grant box from the panel
      container.removeChild(container.childNodes[i]);
      i--;
      cancelGrant(""); // all this function does is iterate missedGrantCount
    }
  }
}

/**
 * When executed on every tick, this will return true for the ticks on an [n]
 * tick interval
 *
 * @param {int} n Interval
 * @returns {boolean} True if current tick is on a valid n interval
 */
function everyinterval(n) {
  if ((myGameArea.frameNo / n) % 1 == 0) {
    return true;
  }
  return false;
}

// ms into string
function parseMillisecondsIntoReadableTime(minutes, speed) {
  var days = minutes / (60 * 24);
  var d = Math.floor(days);
  //Get hours from milliseconds
  var hours = (days - d) * 24;
  var absoluteHours = Math.floor(hours);
  var h = absoluteHours > 9 ? absoluteHours : "0" + absoluteHours;

  //Get remainder from hours and convert to minutes
  var minutes = (hours - absoluteHours) * 60;
  var absoluteMinutes = Math.floor(minutes);
  var m = absoluteMinutes > 9 ? absoluteMinutes : "0" + absoluteMinutes;

  //Get remainder from minutes and convert to seconds
  var seconds = (minutes - absoluteMinutes) * 60;
  var absoluteSeconds = Math.floor(seconds);
  var s = absoluteSeconds > 9 ? absoluteSeconds : "0" + absoluteSeconds;

  if (speed) {
    return d + "d:" + h + "h:" + m + "m " + myGameArea.speed;
  } else {
    return d + "d:" + h + "h:" + m + "m";
  }
}

/**
 * Compares given params to current approvedGrants, and returns true on overlap
 * start time is checked in the outer if statements, and frequency overlap is
 * checked through the function checkFrequency
 *
 * @param {any} startTime
 * @param {any} endTime
 * @param {any} frequency
 * @param {any} bandwidth
 * @returns {any} True if overlap between params and grants in approvedGrants
 */
function checkOverlap(startTime, endTime, frequency, bandwidth) {
  for (i = 0; i < approvedGrants.length; i += 1) {
    if (
      approvedGrants[i].startTime <= startTime &&
      approvedGrants[i].startTime + approvedGrants[i].length >= startTime
    ) {
      if (
        checkFrequency(
          approvedGrants[i].frequency,
          approvedGrants[i].bandwidth,
          frequency,
          bandwidth
        )
      ) {
        return true;
      }
    } else if (
      startTime <= approvedGrants[i].startTime &&
      endTime >= approvedGrants[i].startTime + approvedGrants[i].length
    ) {
      if (
        checkFrequency(
          approvedGrants[i].frequency,
          approvedGrants[i].bandwidth,
          frequency,
          bandwidth
        )
      ) {
        return true;
      }
    } else if (
      approvedGrants[i].startTime >= startTime &&
      approvedGrants[i].startTime <= endTime
    ) {
      if (
        checkFrequency(
          approvedGrants[i].frequency,
          approvedGrants[i].bandwidth,
          frequency,
          bandwidth
        )
      ) {
        return true;
      }
    } else if (
      approvedGrants[i].startTime <= startTime &&
      approvedGrants[i].startTime + approvedGrants[i].length >= endTime
    ) {
      if (
        checkFrequency(
          approvedGrants[i].frequency,
          approvedGrants[i].bandwidth,
          frequency,
          bandwidth
        )
      ) {
        return true;
      }
    }
  }
  return false;
}

/**
 * Returns true on frequency overlap
 *
 * @param {any} freqa
 * @param {any} banda
 * @param {any} freqb
 * @param {any} bandb
 * @returns {boolean} True on freq overlap
 */
function checkFrequency(freqa, banda, freqb, bandb) {
  var la = freqa - banda / 2;
  var ha = freqa + banda / 2;
  var lb = freqb - bandb / 2;
  var hb = freqb + bandb / 2;

  if (
    (lb <= la && hb >= la) ||
    (la <= lb && ha >= hb) ||
    (lb <= ha && hb >= ha) ||
    (lb <= la && hb >= ha)
  ) {
    return true;
  } else {
    return false;
  }
}

/**
 * GrantDiv box and rect generator for the grantList and canvas
 *
 * @param {any} grant Grant to generate grantDiv for
 */
function queueGrant(grant) {
  if (grant.denied) {
    return; // if grant is denied, do not generate grantDiv
  }
  var startFrequency = grant.frequency - grant.bandwidth / 2; // calc start frequency
  var startPlace = frequencyToPixelConversion(startFrequency); // convert startFrequency to pixel coordinates
  var heightOfBlock = bandwidthToComponentHeight(grant.bandwidth); // calc height of block

  // create the grant component
  var queuingGrant = new component(
    grant.length,
    heightOfBlock,
    "pink",
    grant.startTime - myGameArea.frameNo,
    startPlace,
    "select"
  );
  queuingGrant.grant = grant;
  queuedGrantRects.push(queuingGrant); // push onto mygrants
  // if multiple freqs
  if (grant.frequencyb > 0) {
    var startFrequencyb = grant.frequencyb - grant.bandwidth / 2; // calc start frequency
    var startPlaceb = frequencyToPixelConversion(startFrequencyb); // convert startFrequency to pixel coordinates
    queuingGrant = new component(
      grant.length,
      heightOfBlock,
      "pink",
      grant.startTime - myGameArea.frameNo,
      startPlaceb,
      "select"
    );
    queuingGrant.grant = grant;
    queuedGrantRects.push(queuingGrant); // push onto mygrants
  }

  // grantDivs are the grant boxes in the side panel (grantList)
  var grantDiv = document.createElement("div"); // generate new grant box
  grantDiv.classList.add("grantDiv"); // set class to grantDiv
  var abutton = document.createElement("button"); // generate new button
  grantDiv.id = grant.startTime + "." + grant.bandwidth; // set id to startTime + bandwidth !! TODO FIX THIS, REMOVAL OF GRANTDIVS DEPENDS ON ID
  var text = document.createElement("p"); // generate new text
  text.innerHTML =
    "Grant Start Time: " +
    parseMillisecondsIntoReadableTime(
      grant.startTime - nowLinePosition,
      false
    ) +
    " Length: " +
    parseMillisecondsIntoReadableTime(grant.length, false);
  grantDiv.appendChild(text); // add text to grantDiv
  var textb = document.createElement("p"); // generate new text
  textb.innerHTML = "Bandwidth: " + grant.bandwidth / 10 + "MHz";
  grantDiv.appendChild(textb); // add text to grantDiv

  // add text to approve button
  abutton.innerHTML =
    "Approve f<sub>c</sub> " +
    ((baseFrequency + grant.frequency) / 10000).toPrecision(5) +
    "GHz";
  abutton.value = grant; // set value to the current grant ?? this just ends up adding value="[object Object]" ??
  abutton.classList.add("approveButton"); // set class to approveButton

  // onclick listener for approve button
  abutton.addEventListener(
    "click",
    function (e) {
      // does not work when paused
      if (!isPaused) {
        // if the grantDiv being clicked overlaps with any of the approved grants
        if (
          checkOverlap(
            grant.startTime,
            grant.startTime + grant.length,
            grant.frequency,
            grant.bandwidth
          )
        ) {
          // mark the rect as red to indicate failure ??
          convertGrant(
            grant,
            false,
            "red",
            "SU Grant F: " +
            (baseFrequency + grant.frequency) / 10000 +
            "GHz Bandwidth: " +
            grant.bandwidth / 10 +
            "MHz"
          );
          conflictingGrantCount++; // increment conflicting grant count
        } else {
          console.log("approve"); // log success to console ??
          convertGrant(
            grant,
            false,
            "cyan",
            "SU Grant F: " +
            (baseFrequency + grant.frequency) / 10000 +
            "GHz Bandwidth: " +
            grant.bandwidth / 10 +
            "MHz"
          );

          approvedGrantCount++; // increment approved grant count
        }
        approvedGrants.push(grant); // add the current grant to approved grants
        e.currentTarget.parentNode.remove(); // remove the parent node of the approve button (the grantDiv), when it's clicked
      }
    },
    false
  );


  abutton.value = grant; // set value to the current grant ??
  abutton.style.padding = "10px";
  grantDiv.appendChild(abutton); // add button to grantDiv

  // i think frequencyb is an alternative frequency for the grant,
  // if frequencyb is given, another approve button (bbutton) is generated within the grantDiv,
  // to allow the user to approve the grant with a different frequency
  // Redudant code, exact same as abutton
  if (grant.frequencyb > 0) {
    var bbutton = document.createElement("button");

    bbutton.innerHTML =
      "Approve f<sub>c</sub> " +
      ((baseFrequency + grant.frequencyb) / 10000).toPrecision(5) +
      "GHz";
    bbutton.value = grant;
    bbutton.addEventListener(
      "click",
      function (e) {
        if (!isPaused) {
          approvedGrants.push(grant);
          console.log("approve");
          if (
            checkOverlap(
              grant.startTime,
              grant.startTime + grant.length,
              grant.frequency,
              grant.bandwidth
            )
          ) {
            convertGrant(
              grant,
              false,
              "red",
              "SU Grant F: " +
              (baseFrequency + grant.frequencyb) / 10000 +
              "GHz Bandwidth: " +
              grant.bandwidth / 10 +
              "MHz"
            );
            conflictingGrantCount++;
          } else {
            console.log("approve");
            convertGrant(
              grant,
              false,
              "cyan",
              "SU Grant F: " +
              (baseFrequency + grant.frequencyb) / 10000 +
              "GHz Bandwidth: " +
              grant.bandwidth / 10 +
              "MHz"
            );

            approvedGrantCount++;
          }
          e.currentTarget.parentNode.remove();
        }
      },
      false
    );

    bbutton.value = grant;

    bbutton.classList.add("approveButton");
    grantDiv.appendChild(bbutton);
  }
  // deny button
  var dbutton = document.createElement("button");

  dbutton.innerHTML = "Deny";
  dbutton.value = grant;
  dbutton.addEventListener(
    "click",
    function (e) {
      //deny
      if (!isPaused) {
        console.log("deny");
        // queuedGrantRects.forEach(function (grantRect) {
        //   if (grantRect.grant === grant) {
        //     grantRect.width = 0;
        //     grantRect.height = 0;
        //     grantRect.x = 0;
        //     grantRect.y = 0;
        //   }
        // });
        grant.denied = true;
        deniedGrantCount++;
        e.currentTarget.parentNode.remove();
      }
    },
    false
  );
  dbutton.value = grant;
  dbutton.classList.add("denyButton");

  grantDiv.appendChild(dbutton);

  var container = document.getElementById("grantList");
  container.appendChild(grantDiv);
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

/**
 * Calls convertGrant to add the grant to myGrants and grantText, then adds
 * grant to approvedGrants[]
 *
 * @param {any} grant To action upon
 */
function makePUGrant(grant) {
  convertGrant(
    grant,
    false,
    "green",
    "PU Grant F: " +
    (baseFrequency + grant.frequency) / 10000 +
    "GHz Bw: " +
    grant.bandwidth / 10 +
    "MHz"
  );
  approvedGrants.push(grant);
}

/**
 * Translates grant object into a rect component and text component, then adds
 * them to the myGrants and movingTexts arrays
 *
 * @param {grant} grant Grant to draw
 * @param {boolean} b If true, use frequency B, if false, use frequency A
 * @param {string} color
 * @param {string} text To draw over grant rect in the canvas
 */
function convertGrant(grant, b, color, text) {
  // redundant if block, can be replaced with unary operators
  if (b) {
    //use frequency b
    var startFrequency = grant.frequencyb - grant.bandwidth / 2; // calc start frequency
    var startPlace = frequencyToPixelConversion(startFrequency); // convert startFrequency to pixel coordinates
    var heightOfBlock = bandwidthToComponentHeight(grant.bandwidth); // calc height of block

    // create the grant component
    var approvedGrant = new component(
      grant.length,
      heightOfBlock,
      color,
      grant.startTime - myGameArea.frameNo,
      startPlace
    );
    myGrants.push(approvedGrant); // push onto mygrants
    // generate the text for the grant component
    grantText = new component(
      "20px",
      "Consolas",
      "black",
      grant.startTime - myGameArea.frameNo,
      startPlace + heightOfBlock / 2,
      "text"
    );
    grantText.text = text; // set text value
    movingTexts.push(grantText); // append to array of moving texts
  } else {
    // not commented as it is redundant, look above
    //use frequency a
    var startFrequency = grant.frequency - grant.bandwidth / 2;
    var startPlace = frequencyToPixelConversion(startFrequency);
    var heightOfBlock = bandwidthToComponentHeight(grant.bandwidth);

    var approvedGrant = new component(
      grant.length,
      heightOfBlock,
      color,
      grant.startTime - myGameArea.frameNo,
      startPlace
    );
    console.log(grant);
    myGrants.push(approvedGrant);
    grantText = new component(
      "20px",
      "Consolas",
      "black",
      grant.startTime - myGameArea.frameNo,
      startPlace + heightOfBlock / 2,
      "text"
    );
    grantText.text = text;
    movingTexts.push(grantText);
  }
}

/**
 * Increments conflictingGrantCount
 *
 * @param {any} grant Unused var
 */
function conflictGrant(grant) {
  conflictingGrantCount++;
}
// increments missedGrantCount
function cancelGrant(grant) {
  missedGrantCount++;
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
// change frame timings to speed up game
function setFrameInterval(speed) {
  myGameArea.speed = 1 / speed + "x";
  clearInterval(myGameArea.interval);
  myGameArea.interval = setInterval(updateGameArea, speed * 20);
}

function restart() {
  location.reload();
}

// ??
function overlayOn() {
  document.getElementById("overlay").style.display = "block";

  document.getElementById("informationHTML").style.visibility = "visible";

  document.getElementById("infoClose").style.visibility = "visible";
}

// ??
function overlayOff() {
  document.getElementById("overlay").style.display = "none";

  document.getElementById("informationHTML").style.visibility = "hidden";

  document.getElementById("infoClose").style.visibility = "hidden";
}
