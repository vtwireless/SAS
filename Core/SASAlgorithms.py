import WinnForum
import time
from datetime import datetime, timedelta

class SASAlgorithms:
    def __init__(self):
        self.grantAlgorithm = 'DEFAULT'
        self.REMAlgorithm = 'DEFAULT' #DEFAULT = EQUALWEIGHT, CELLS, TRUSTED, TRUST SCORE, RADIUS
        self.defaultHeartbeatInterval = 5
        self.threshold = -30.0 #POWER THRESHOLD
        self.longitude = -80.4 #Blacksburg location
        self.latitude = 37.2
        self.radius = 1000#Kilometers
        self.maxGrantTime = 300#seconds
        self.ignoringREM = True

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
        if heartbeat["grantRenew"] == True:
            response.transmitExpireTime = self.calculateGrantExpireTime(grants, REM, grant)
        response.grantExpireTime = self.calculateGrantExpireTime(grants, REM, grant)
        response.heartbeatInterval = self.getHeartbeatIntervalForGrantId(grant.id) | self.getHeartbeatInterval()
        lowFreq = self.getLowFreqFromOP(grant.operationParam)
        highFreq = self.getHighFreqFromOP(grant.operationParam)
        fr = WinnForum.FrequencyRange(lowFreq, highFreq)
        response.operationParam = WinnForum.OperationParam(30, fr)
        longitude = None
        latitude = None
        radius = None
        if grant.vtGrantParams:
            longLat = grant.vtGrantParams.location.spit(",")
            longitude = longLat[0]
            latitude = longLat[1]
            radius = 1000
        present = self.isPUPresentREM(REM, highFreq, lowFreq, latitude, longitude, radius)
        if present and not self.ignoringREM:
            response.transmitExpireTime = datetime.now().strftime("%Y%m%dT%H:%M:%S%Z")
            response.response = self.generateResponse(401)#Grant conflict
        else:
            response.response = self.generateResponse(0)
        return response

    def isGrantSuspended(self):
        #return "SUSPENDED_GRANT"
        return "SUCCESS"

    def defaultGrantAlg(self, grants, REM, request):
        gr = WinnForum.GrantResponse()
        gr.grantId = None
        gr.cbsdId = request.cbsdId
        gr.grantExpireTime = self.calculateGrantExpireTime(grants, REM, None)
        gr.heartbeatInterval = self.getHeartbeatIntervalForGrantId(gr.grantId)
        gr.measReportConfig = "MEASREPORTCONFIG"
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
        response = WinnForum.Response(responseCode, WinnForum.responseDecode(responseCode))
        return response

    def isPUPresentREM(self, REM, highFreq, lowFreq, latitude, longitude, radius):
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
            print("Currently no spectrum data")
            return True
        if self.getREMAlgorithm() == 'DEFAULT':
            return self.defaultREMAlgorith(remData)
        elif self.getREMAlgorithm() == 'TRUSTSCORE':
            return self.trustScoreREMAlgorithm(remData)
        elif self.getREMAlgorithm() == 'TRUSTED':
            return self.trustedREMAlgorithm(remData)
        else:
            return False

    def calculateGrantExpireTime(self, grants, REM, grant):
        grantCount = len(grants)
        t = datetime.now()
        if grantCount <= 1:
            t = t + timedelta(seconds = self.maxGrantTime)
            return t.strftime("%Y%m%dT%H:%M:%S%Z")
        else:
            t = t + timedelta(seconds = self.defaultHeartbeatInterval * 2)
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
        for object in remData:
            total = total + float(object.powerLevel)
            
        if (total*1.0/len(remData)) > self.threshold:
            return True
        else:
            return False

    def trustScoreREMAlgorithm(self, remData):
        #Trust scores with threshold parameter, no location, all parameters
        total = 0.0
        trustScoreThreshold = 5.0
        for object in remData:
            if float(object.powerLevel) > self.threshold:#if the individual power level sensed is geater than threshold
                total = total + object.cbsd.trustScore
        if (total*1.0/len(remData)) > trustScoreThreshold:
            return True
        else:
            return False

    def trustedREMAlgorithm(self, remData):
       #Trust scores with threshold parameter, no location, all parameters
        count = 0
        total = 0.0
        trustCutoff = 7.0 #don't count if less than score
        for object in remData:
            if object.cbsd.trustScore > trustCutoff:
                total = total + float(object.powerLevel)
                count = count + 1
        if (total*1.0/count) > self.threshold:
            return True
        else:
            return False


    def acceptableRange(self, lowFreq, highFreq):
        if lowFreq < highFreq and lowFreq >= 3550000000 and highFreq <= 3700000000:
            return True
        else:
            return False