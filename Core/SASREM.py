from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

class SASREM:
    def __init__(self):
        self.nodes = []
        self.objects = []
        self.regions = []
        self.secondsAgo = 5

    def addREMObject(self, object):
        self.objects.append(object)
        # print(self.objects)
    
    def removeREMObject(self, object):
        self.objects.remove(object)

    def addRegion(self, region):
        self.regions.append(region)
    
    def removeRegionObject(self, region):
        self.regions.remove(region)

    def clearOldData(self, now, secondsAgo):
        for object in self.objects:
            if object.timeStamp < (now - datetime.timedelta(seconds = secondsAgo)):
                self.objects.remove(object)

    #Tell nodes to sense data, actively
    def senseRegionWithParameters(self, longitude, latitude, highFrequency, lowFrequency, radius):
        objectsToSend = []
        for node in self.nodes:
            if self.isWithinRegion(latitude, longitude, radius, node.latitude, node.longitude):
                objectsToSend.append(object)
                #ask for information
                #add it
                print('in')
        return objectsToSend

    #Get data without telling nodes specficially to get, passive
    def getSpectrumDataWithParameters(self, longitude, latitude, highFrequency, lowFrequency, radius):
        objectsToSend = []
        for object in self.objects:
            if not object.longitude and not object.longitude:
                objectsToSend.append(object)
            elif self.isWithinRegion(latitude, longitude, radius, object.latitude, object.longitude):
                objectsToSend.append(object)
            if object.timeStamp < (datetime.now() - timedelta(seconds = self.secondsAgo)):
                self.objects.remove(object)

        return objectsToSend



    def isWithinRegion(self, centerLatitude, centerLongitude, radius, pointLatitude, pointLongitude):
    # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [centerLongitude, centerLatitude, float(pointLongitude), float(pointLatitude)])
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
        if cbsd:
            freq = measReport.measFrequency
            band = measReport.measBandwidth
            power = measReport.measRcvdPower
            obj = SASREMObject(cbsd.longitude, cbsd.latitude, cbsd, power, str(float(freq)+float(band)), freq, datetime.now())
            self.addREMObject(obj)

    def getDistance(self, centerLatitude, centerLongitude, pointLatitude, pointLongitude):
    # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [centerLongitude, centerLatitude, float(pointLongitude), float(pointLatitude)])
    # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
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

class REMRegion:
    def __init__(self, longitude, latitude, radius):
        self.longitude = longitude
        self.latitude = latitude
        self.radius = radius

class REMPoint:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

class CBSDSocket:
    def __init__(self, cbsdId, sid, justChangedParams):
        self.cbsdId = cbsdId
        self.sid = sid
        self.justChangedParams = justChangedParams
