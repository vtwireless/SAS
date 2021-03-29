import WinnForum
import time
from datetime import datetime, timedelta, timezone
import threading

class SASAlgorithms:
    MINCBRSFREQ = 3550000000
    MAXCBRSFREQ = 3700000000
    TENMHZ = 10000000
    def __init__(self):
        self.grantAlgorithm = 'DEFAULT'
        self.REMAlgorithm = 'DEFAULT' #DEFAULT = EQUALWEIGHT, CELLS, TRUSTED, TRUST SCORE, RADIUS
        self.defaultHeartbeatInterval = 5
        self.threshold = 10.0 #POWER THRESHOLD
        self.longitude = -80.4 #Blacksburg location
        self.latitude = 37.2
        self.radius = 1000#Kilometers
        self.maxGrantTime = 300#seconds
        self.ignoringREM = True
        self.offerNewParams = True
        self.maxEIRP = 30

    def setGrantAlgorithm(self, algorithm):
        self.grantAlgorithm = algorithm

    def setREMAlgorithm(self, algorithm):
        self.REMAlgorithm = algorithm

    def setHeartbeatInterval(self, heartbeatInterval):
        self.defaultHeartbeatInterval = heartbeatInterval

    def getGrantAlgorithm(self):
        return self.grantAlgorithm

    def getREMAlgorithm(self):
        return self.REMAlgorithm
    
    def getHeartbeatInterval(self):
        return self.defaultHeartbeatInterval

    def getHeartbeatIntervalForGrantId(self, grantId):
        #TODO change
        return self.defaultHeartbeatInterval

    def getMaxEIRP(self):
        return self.maxEIRP


    def runGrantAlgorithm(self, grants, REM, request):
        grantResponse = WinnForum.GrantResponse()
        if not self.acceptableRange(self.getLowFreqFromOP(request.operationParam), self.getHighFreqFromOP(request.operationParam)):
            grantResponse.response = self.generateResponse(103)
            grantResponse.response.responseData = "Frequency range outside of license"
            return grantResponse
        elif self.grantAlgorithm == 'DEFAULT':
            grantResponse = self.defaultGrantAlg(grants, REM, request)
        elif self.grantAlgorithm =='TIER':
            grantResponse = self.tierGrantAlg(grants, REM, request)
        return grantResponse

    def runHeartbeatAlgorithm(self, grants, REM, heartbeat, grant):
        response = WinnForum.HeartbeatResponse()
        if not grant:
            response.response = self.generateResponse(103)
            return response
        response.cbsdId = grant.cbsdId
        response.grantId = grant.id
        if "grantRenew" in heartbeat:
            if heartbeat["grantRenew"] == True:
                response.grantExpireTime= self.calculateGrantExpireTime(grants, REM, grant, True)
            else:
                response.grantExpireTime = self.calculateGrantExpireTime(grants, REM, grant, False)
        response.transmitExpireTime = self.calculateGrantExpireTime(grants, REM, grant, False)
        response.heartbeatInterval = self.getHeartbeatIntervalForGrantId(grant.id) or self.getHeartbeatInterval()
        lowFreq = self.getLowFreqFromOP(grant.operationParam)
        highFreq = self.getHighFreqFromOP(grant.operationParam)
        fr = WinnForum.FrequencyRange(lowFreq, highFreq)
        response.operationParam = WinnForum.OperationParam(self.getMaxEIRP(), fr)
        longitude = None
        latitude = None
        radius = None
        if grant.vtGrantParams:
            longLat = grant.vtGrantParams.location.split(",")
            longitude = float(longLat[0])
            latitude = float(longLat[1])
            radius = 1000
        present = self.isPUPresentREM(REM, highFreq, lowFreq, latitude, longitude, radius)
        if present == 1 and not self.ignoringREM:
            response.transmitExpireTime = datetime.now(timezone.utc).strftime("%Y%m%dT%H:%M:%S%Z")
            response.response = self.generateResponse(501)#Suspended Grant
        else:
            response.response = self.generateResponse(0)
            if self.offerNewParams:
                freqRange = self.MAXCBRSFREQ - self.MINCBRSFREQ
                blocks = freqRange/self.TENMHZ
                for i in range(int(blocks)):
                    low = (i * self.TENMHZ) + self.MINCBRSFREQ
                    high = ((i + 1) * self.TENMHZ) + self.MINCBRSFREQ
                    result = self.isPUPresentREM(REM, low, high, latitude, longitude, radius)
                    if result == 0:
                        op = WinnForum.OperationParam(self.getMaxEIRP(), WinnForum.FrequencyRange(low, high))
                        tempFakeGrant = WinnForum.Grant(0, 0, op)
                        tempFakeGrantResponse = self.runGrantAlgorithm(grants, REM, tempFakeGrant)
                        if tempFakeGrantResponse.response.responseCode == 0:
                            response.operationParam = op
        return response

    def isGrantSuspended(self):
        #return "SUSPENDED_GRANT"
        return "SUCCESS"

    def defaultGrantAlg(self, grants, REM, request):
        gr = WinnForum.GrantResponse()
        gr.grantId = None
        gr.cbsdId = request.cbsdId
        gr.grantExpireTime = self.calculateGrantExpireTime(grants, REM, None, True)
        gr.heartbeatInterval = self.getHeartbeatIntervalForGrantId(gr.grantId)
        gr.measReportConfig = ["RECEIVED_POWER_WITH_GRANT", "RECEIVED_POWER_WITHOUT_GRANT"]
        conflict = False
        for grant in grants:
            rangea = self.getHighFreqFromOP(grant.operationParam)
            rangeb = self.getLowFreqFromOP(grant.operationParam)
            freqa = self.getHighFreqFromOP(request.operationParam)
            freqb = self.getLowFreqFromOP(request.operationParam)
            if self.frequencyOverlap(freqa, freqb, rangea, rangeb):
                conflict = True
        if conflict == True:
            gr.response = self.generateResponse(401)
        else:
            gr.response = self.generateResponse(0)
            gr.operationParam = request.operationParam
        gr.channelType = "GAA"
        return gr

    def tierGrantAlg(self, grants, REM, request):
        return True

    def generateResponse(self, responseCode):
        response = WinnForum.Response(str(responseCode), WinnForum.responseDecode(responseCode))
        return response

    def isPUPresentREM(self, REM, highFreq, lowFreq, latitude, longitude, radius):
        #Return 0 = not present, 1 = present, 2 = no spectrum data, 3 = error with alorithm select
        latit = self.latitude
        longit = self.longitude
        rad = self.radius
        if latitude != None and longitude != None:
            longit = longitude
            latit = latitude
        if radius != None:
            rad = radius
        remData = REM.getSpectrumDataWithParameters(longit, latit, highFreq, lowFreq, rad)#GET ALL  REM DATA
        if not remData:
            #print("Currently no spectrum data") # TODO: remove comment
            return 2
        if self.getREMAlgorithm() == 'DEFAULT':
            if self.defaultREMAlgorith(remData):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'TRUSTSCORE':
            if self.trustScoreREMAlgorithm(remData):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'TRUSTED':
            if self.trustedREMAlgorithm(remData):
                return 1
            else:
                return 0
        else:
            return 3

    def calculateGrantExpireTime(self, grants, REM, grant, renew):
        grantCount = len(grants)
        t = datetime.now(timezone.utc)
        if grantCount <= 1:
            t = t + timedelta(seconds = self.maxGrantTime)
            return t.strftime("%Y%m%dT%H:%M:%S%Z")
        else:
            t = t + timedelta(seconds = (self.defaultHeartbeatInterval * 2))
            return t.strftime("%Y%m%dT%H:%M:%S%Z")

    def getHighFreqFromOP(self, params):
        return params.operationFrequencyRange.highFrequency
    
    def getLowFreqFromOP(self, params):
        return params.operationFrequencyRange.lowFrequency

    def frequencyOverlap(self, freqa, freqb, rangea, rangeb):
        if (freqa <= rangea and freqb <= rangeb):
            return True
        elif (freqa >= rangea and freqb <= rangeb):
            return True
        elif (freqa <= rangeb and freqb >= rangeb):
            return True
        elif (freqa <= rangea and freqb >= rangeb):
            return True
        else:
            return False


    def defaultREMAlgorith(self, remData):
        total = 0.0
        #Equal weight with threshold parameter, no location, all parameters
        for data_point in remData:
            total = total + float(data_point.powerLevel)
            
        if (total*1.0/len(remData)) > self.threshold:
            return True
        else:
            return False

    def trustScoreREMAlgorithm(self, remData):
        #Trust scores with threshold parameter, no location, all parameters
        total = 0.0
        trustScoreThreshold = 5.0
        for data_point in remData:
            if float(data_point.powerLevel) > self.threshold:#if the individual power level sensed is geater than threshold
                total = total + data_point.cbsd.trustScore
        if (total*1.0/len(remData)) > trustScoreThreshold:
            return True
        else:
            return False

    def trustedREMAlgorithm(self, remData):
       #Trust scores with threshold parameter, no location, all parameters
        count = 0
        total = 0.0
        trustCutoff = 7.0 #don't count if less than score
        for data_point in remData:
            if data_point.cbsd.trustScore > trustCutoff:
                total = total + float(data_point.powerLevel)
                count = count + 1
        if (total*1.0/count) > self.threshold:
            return True
        else:
            return False


    def acceptableRange(self, lowFreq, highFreq):
        if((lowFreq < highFreq) and (lowFreq >= self.MINCBRSFREQ) and (highFreq <= self.MAXCBRSFREQ)):
            return True
        else:
            return False
