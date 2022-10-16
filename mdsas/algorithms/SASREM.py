from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt


class SASREM:
    """SASREM"""

    def __init__(self):
        self.nodes = []
        self.objects = []
        self.secondsAgo = 5
        self.cells = []

    def makeCells(self, latitude, longitude, numberOfCells, radius):
        """
        Create REM cells and add them to the REM
        Parameters
        ----------
        latitude
        longitude
        numberOfCells
        radius: in KM

        Returns
        -------

        """
        cellWidth = radius
        rows = int(sqrt(numberOfCells))
        self.cells = []
        id = 0
        if (rows % 2) == 0:  # even
            for x in range(rows):
                for y in range(rows):
                    startx = ((x - int(rows / 2) + 0.5) * cellWidth) + longitude
                    starty = ((y - int(rows / 2) + 0.5) * cellWidth) + latitude
                    point = REMPoint(starty, startx)
                    rc = REMCell(id, point, cellWidth)
                    id = id + 1
                    self.cells.append(rc)
        else:
            for x in range(rows):
                for y in range(rows):
                    startx = ((x - int(rows / 2)) * cellWidth) + longitude
                    starty = ((y - int(rows / 2)) * cellWidth) + latitude
                    point = REMPoint(starty, startx)
                    rc = REMCell(id, point, cellWidth)
                    id = id + 1
                    self.cells.append(rc)

    def addREMObject(self, object):
        self.objects.append(object)
        # print(self.objects)

    def removeREMObject(self, object):
        self.objects.remove(object)

    def clearOldData(self, now, secondsAgo):
        for object in self.objects:
            if object.timeStamp < (now - timedelta(seconds=secondsAgo)):
                self.objects.remove(object)

    # Tell nodes to sense data, actively
    # TODO: Incomplete Implementation
    def senseRegionWithParameters(self, longitude, latitude, highFrequency, lowFrequency, radius):
        objectsToSend = []
        for node in self.nodes:
            if self.isWithinRegion(latitude, longitude, radius, node.latitude, node.longitude):
                objectsToSend.append(object)
                # ask for information
                # add it
                print('in')
        return objectsToSend

    # Get data without telling nodes specifically to get, passive
    def getSpectrumDataWithParameters(self, longitude, latitude, highFrequency, lowFrequency, radius):
        objectsToSend = []
        for object in self.objects:
            overlapping = self.frequencyOverlap(float(object.lowFrequency), float(object.highFrequency),
                                                float(lowFrequency), float(highFrequency))
            if not object.longitude and not object.longitude and overlapping:
                objectsToSend.append(object)
            elif self.isWithinRegion(latitude, longitude, radius, object.latitude, object.longitude) and overlapping:
                objectsToSend.append(object)
            if object.timeStamp < (datetime.now() - timedelta(seconds=self.secondsAgo)):
                self.objects.remove(object)

        return objectsToSend

    def frequencyOverlap(self, freqa, freqb, rangea, rangeb):
        """Checks to see if freq is within range"""
        if freqa <= rangea <= freqb:
            return True
        elif freqa >= rangea and freqb <= rangeb:
            return True
        elif freqa <= rangeb <= freqb:
            return True
        elif freqa <= rangea and freqb >= rangeb:
            return True
        else:
            return False

    def isWithinRegion(self, centerLatitude, centerLongitude, radius, pointLatitude, pointLongitude):
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians,
                                     [centerLongitude, centerLatitude, float(pointLongitude), float(pointLatitude)])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        calculatedRadius = c * r
        if calculatedRadius <= radius:
            return True
        else:
            return False

    def findPU(self):
        # find local max or local min
        return REMPoint(-80, 35)

    def measReportToSASREMObject(self, measReport, cbsd):
        if cbsd:
            freq = measReport.measFrequency
            band = measReport.measBandwidth
            power = measReport.measRcvdPower
            obj = SASREMObject(cbsd.longitude, cbsd.latitude, cbsd, power, str(float(freq) + float(band)), freq,
                               datetime.now())
            self.addREMObject(obj)

    def getDistance(self, centerLatitude, centerLongitude, pointLatitude, pointLongitude):
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians,
                                     [centerLongitude, centerLatitude, float(pointLongitude), float(pointLatitude)])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        calculatedRadius = c * r
        return calculatedRadius

    def findClosestSecureNode(self, latitude, longitude, cbsds, distance):
        cbsdToReturn = None
        minDist = distance
        for cbsd in cbsds:
            if cbsd.fullyTrusted == True:
                dist = self.getDistance(latitude, longitude, cbsd.latitude, cbsd.longitude)
                if dist <= distance:
                    if minDist >= dist:
                        cbsdToReturn = cbsd
                        minDist = dist
        return cbsdToReturn


class SASREMObject:
    def __init__(self, longitude, latitude, cbsd, powerLevel, highFrequency, lowFrequency, timeStamp):
        self.longitude = longitude
        self.latitude = latitude
        self.cbsd = cbsd
        self.powerLevel = powerLevel
        self.highFrequency = highFrequency
        self.lowFrequency = lowFrequency
        self.timeStamp = timeStamp


class REMPoint:
    def __init__(self, latitude, longitude):
        self.longitude = longitude
        self.latitude = latitude


class CBSDSocket:
    def __init__(self, cbsdId, sid, justChangedParams):
        self.cbsdId = cbsdId
        self.sid = sid
        self.justChangedParams = justChangedParams


class REMCell:
    def __init__(self, id, centerPoint, diameter):
        self.id = id
        self.centerPoint = centerPoint
        self.diameter = diameter
        self.data = []
        self.variance = 0
        self.best = False
        self.worst = False

    def isInCell(self, dataPoint):
        lat = dataPoint.cbsd.latitude
        lon = dataPoint.cbsd.longitude

        if ((self.centerPoint.latitude - self.diameter) <= lat <= (self.centerPoint.latitude + self.diameter) and
                (self.centerPoint.longitude - self.diameter) <= lon <= (self.centerPoint.longitude + self.diameter)):
            return True
        else:
            return False
