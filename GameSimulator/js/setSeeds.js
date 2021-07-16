// dynamic loading of csv data

const setSeedFilenames = [
    "setSeeds/1.csv",
    "setSeeds/2.csv"
];

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
        callback(setSeed);

    }

}
