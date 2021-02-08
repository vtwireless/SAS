import time
from math import radians, cos, sin, asin, sqrt

class SASREM:
    def __init__(self):
        self.nodes = []
        self.objects = []
        self.regions = []

    def addREMObject(self, object):
        self.objects.append(object)
        print(self.objects)
    
    def removeREMObject(self, object):
        self.objects.remove(object)

    def addRegion(self, region):
        self.regions.append(region)
    
    def removeRegionObject(self, region):
        self.regions.remove(region)

    def clearOldData(self, now, secondsAgo):
        for object in self.objects:
            if object.timeStamp < (now - secondsAgo):
                self.objects.remove(object)

    #Tell nodes to sense data, actively
    def senseRegionWithParameters(self, longitude, latitude, highFrequency, lowFrequency, radius):
        objectsToSend = []
        for node in self.nodes:
            if self.isWithinRegion(longitude, latitude, radius, node.longitude, node.latitude):
                #objectsToSend.append(object)
                #ask for information
                #add it
                print('in')
        return objectsToSend

    #Get data without telling nodes specficially to get, passive
    def getSpectrumDataWithParameters(self, longitude, latitude, highFrequency, lowFrequency, radius):
        objectsToSend = []
        for object in self.objects:
            if self.isWithinRegion(longitude, latitude, radius, object.longitude, object.latitude):
                objectsToSend.append(object)
        return objectsToSend



    def isWithinRegion(self, centerLongitude, centerLatitude, radius, pointLongitude, pointLatitude):
    # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [centerLongitude, centerLatitude, pointLongitude, pointLatitude])
    # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        calculatedRadius = c * r
        if calculatedRadius <= radius:
            return True
        else:
            return False

    def findPU(self):
        #find local max or local min
        return REMPoint(-80, 35)

    def measReportToSASREMObject(self, measReport, cbsd):
        rcvd = measReport.measFrequency[0]
        freq = rcvd.measFrequency
        band = rcvd.measBandwidth
        power = rcvd.measRcvdPower
        obj = SASREMObject(cbsd.longitude, cbsd.latitude, cbsd, power, freq+band, freq, time.time())
        self.addREMObject(obj)


class SASREMObject:
    def __init__(self, longitude, latitude, cbsd, powerLevel, highFrequency, lowFrequency, timeStamp):
        self.longitude = longitude
        self.latitude = latitude
        self.cbsd = cbsd
        self.powerLevel = powerLevel
        self.highFrequency = highFrequency
        self.lowFrequency = lowFrequency
        self.timeStamp = timeStamp

class REMRegion:
    def __init__(self, longitude, latitude, radius):
        self.longitude = longitude
        self.latitude = latitude
        self.radius = radius

class REMPoint:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    