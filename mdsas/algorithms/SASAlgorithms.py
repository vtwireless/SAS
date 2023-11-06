import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import Server_WinnForum as WinnForum
from datetime import datetime, timedelta, timezone
import numpy


class SASAlgorithms:
    """
    This class determines the parameters and algorithms used by the SAS
    """
    MINCBRSFREQ = 3550000000
    MAXCBRSFREQ = 3700000000
    TENMHZ = 10000000
    DEFAULT_TIME_FORMAT = "%Y-%m-%dT%H:%M"

    def __init__(self):
        self.grantAlgorithm = 'DEFAULT'
        self.REMAlgorithm = 'DEFAULT'  # DEFAULT = EQUALWEIGHT, CELLS, TRUSTED, TRUST SCORE, RADIUS
        self.defaultHeartbeatInterval = 20
        self.retryInterval = 30
        self.transmitExpireTime = 240
        self.minimumGrantSize = self.TENMHZ / 2
        self.maximumGrantSize = 15 * self.TENMHZ
        self.defaultChannelSize = self.TENMHZ

        self.threshold = 30.0  # POWER THRESHOLD
        self.longitude = -80.4  # Blacksburg location
        self.latitude = 37.2
        self.radius = 1000  # Kilometers
        self.maxGrantTime = 300  # seconds
        self.ignoringREM = True
        self.offerNewParams = True
        self.maxEIRP = 30
        self.interferenceThresholdBm = -100
        self.cells = []

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
        # TODO change
        return self.defaultHeartbeatInterval

    def getMaxEIRP(self):
        return self.maxEIRP

    def calculateDistance(self, a, b):
        lat1, lon1 = a
        lat2, lon2 = b
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d
    
    def calculateInterferenceRadius(self, request):
        transmission_power_dBm = request.operationParam.maxEirp
        # Calulate the interference radius based on the request
        # PL(d)=15+36log10d (3.5 GHz)
        # https://ieeexplore-ieee-org.ezproxy.lib.vt.edu/document/4735242
        path_loss = transmission_power_dBm - self.interferenceThresholdBm
        log10_distance = (path_loss - 15) / 36
        distance = 10 ** log10_distance
        return distance

    def get_center_freq(self, channel):
        channel_width = 10.0e6  # The width of each channel in MHz.
        base_freq = 3550.0e6  # The frequency of the first channel in MHz.

        # Calculate the center frequency of the specified channel using the formula:
        # centerFreq = baseFreq + (channel * channelWidth) + (channelWidth / 2.0)
        center_freq = base_freq + (channel * channel_width) + (channel_width / 2.0)

        # Return the center frequency to the caller.
        return center_freq

    def get_freq_range(self, channel):
        center_freq = self.get_center_freq(channel)
        channel_width = 10.0e6  # The width of each channel in MHz.

        # Calculate the low and high frequencies for the specified channel
        freq_low = center_freq - (channel_width / 2.0)
        freq_high = center_freq + (channel_width / 2.0)

        # Return the low and high frequencies as a tuple
        return freq_low, freq_high

    def runGrantAlgorithm(self, grants, REM, request, CbsdList, SpectrumList, socket):
        grantResponse = WinnForum.GrantResponse()
        IsPAL = False
        for i, cbsd in enumerate(CbsdList):
                if(cbsd['cbsdId'] == request.cbsdId):
                    if(cbsd['accessPriority'] == "PAL"):
                        IsPAL = True
        
        lowFreq, highFreq = self.getLowFreqFromOP(request.operationParam), self.getHighFreqFromOP(
            request.operationParam)

        if not self.acceptableRange(lowFreq, highFreq):
            grantResponse.response = self.generateResponse(103)
            grantResponse.response.responseData = "Frequency range outside of license"
            return grantResponse

        elif not self.acceptableBandwidth(lowFreq, highFreq):
            grantResponse.response = self.generateResponse(103)
            grantResponse.response.responseData = "Max Channel Size is " + str(self.defaultChannelSize)
            return grantResponse

        if self.grantAlgorithm == 'DEFAULT':
            grantResponse = self.defaultGrantAlg(grants, request, IsPAL, CbsdList, SpectrumList, socket)
        elif self.grantAlgorithm == 'TIER':
            grantResponse = self.tierGrantAlg(grants, REM, request)
        return grantResponse

    def createDPAGrant(self, dpa, grants, CbsdList, SpectrumList, socket):
        grantResponse = WinnForum.GrantResponse()
        grantRequest = WinnForum.GrantRequest(dpa["id"], None)
        ofr = WinnForum.FrequencyRange(dpa["spectrum"][0][0], dpa["spectrum"][0][1])
        op = WinnForum.OperationParam(30, ofr)
        grantRequest.operationParam = op
        # request = { "cbsdId" : dpa["id"], "operationParam": { "operationFrequencyRange": { "lowFrequency": dpa["spectrum"][0][0], "highFrequency": dpa["spectrum"][0][1] } } }
        grantRequest.lat = dpa["latitude"]
        grantRequest.long = dpa["longitude"]
        grantRequest.IsDPA = True
        grantRequest.dist = dpa["radius"]
        grantResponse = self.defaultGrantAlg(grants, grantRequest, True, CbsdList, SpectrumList, socket)
        g = WinnForum.Grant(grantResponse.grantId, dpa["id"], grantResponse.operationParam, None, grantResponse.grantExpireTime)
        g.IsDpa = True
        g.lat = dpa["latitude"]
        g.long = dpa["longitude"]
        g.id = dpa["id"]
        g.dist = dpa["radius"] 
        return g
    
    # Create a incumbent grant
    def createIncumbentGrant(self, sensorInfo, channel, grants, CbsdList, SpectrumList, socket):
        sensorId = sensorInfo["sensor_id"]
        sensorLat = sensorInfo["lat"]
        sensorLon = sensorInfo["lon"]

        t = datetime.now(timezone.utc)
        t = t + timedelta(seconds = self.maxGrantTime)
        ExpiryTime = t.strftime("%Y%m%dT%H:%M:%S%Z")

        grantResponse = WinnForum.GrantResponse()
        frequency_low, frequency_high = self.get_freq_range(channel)
        
        grantRequest = WinnForum.GrantRequest(f"incumbent-{sensorId}-channel{channel}", None)
        ofr = WinnForum.FrequencyRange(frequency_low, frequency_high)
        op = WinnForum.OperationParam(30, ofr)
        grantRequest.operationParam = op
        
        grantRequest.lat = sensorLat
        grantRequest.long = sensorLon
        
        grantRequest.dist = 1000
        grantResponse.grantExpireTime = ExpiryTime
        grantResponse = self.defaultGrantAlg(grants, grantRequest, True, CbsdList, SpectrumList, socket)
        g = WinnForum.Grant(grantResponse.grantId, f"incumbent-{sensorId}-channel{channel}", grantResponse.operationParam, None, grantResponse.grantExpireTime)
        
        g.lat = sensorLat
        g.long = sensorLon
        
        g.id = f"incumbent-{sensorId}-channel{channel}"
        
        g.dist = 1000
        
        return g

    def runHeartbeatAlgorithm(self, grants, REM, heartbeat, grant):
        response = WinnForum.HeartbeatResponse()
        if not grant:
            response.response = self.generateResponse(103)
            return response
        response.cbsdId = grant.cbsdId
        response.grantId = grant.id
        if(hasattr(grant, 'status')):
            if grant.status == "TERMINATED":
                response.response = self.generateResponse(501)
                return response
        
        if "grantRenew" in heartbeat:
            if heartbeat["grantRenew"] == True:
                response.grantExpireTime = self.calculateGrantExpireTime(grants, REM, grant, True)
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
            response.response = self.generateResponse(501)  # Suspended Grant
        else:
            response.response = self.generateResponse(0)
            if self.offerNewParams:
                freqRange = self.MAXCBRSFREQ - self.MINCBRSFREQ
                blocks = freqRange / self.TENMHZ
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
        # return "SUSPENDED_GRANT"
        return "SUCCESS"

    def defaultGrantAlg(self, grants, REM, request, IsPAL, CbsdList, SpectrumList, socket):
        gr = WinnForum.GrantResponse()
        gr.grantId = None
        # gr.cbsdId = request.cbsdId
        gr.grantExpireTime = self.calculateGrantExpireTime(grants, REM, None, True, request)
        gr.heartbeatInterval = self.getHeartbeatIntervalForGrantId(gr.grantId)
        gr.measReportConfig = ["RECEIVED_POWER_WITH_GRANT", "RECEIVED_POWER_WITHOUT_GRANT"]
        conflict = False
        for grant in list(grants):
            if hasattr(grant, 'status'):
                if grant.status == "TERMINATED":
                    print("Skipping terminated grant")
                    continue
            
            rangea = grant["maxFrequency"]
            rangeb = grant["minFrequency"]
            freqa = self.getHighFreqFromOP(request.operationParam)
            freqb = self.getLowFreqFromOP(request.operationParam)

            dist = self.calculateDistance((grant.lat, grant.long), (request.lat, request.long)) * 1000
            print("Distance: " + str(dist))
            print("Grant Distance: " + str(grant.dist))
            print("Request Distance: " + str(request.dist))

            if self.frequencyOverlap(freqa, freqb, rangea, rangeb):
                if IsPAL:
                    if(dist < grant.dist or dist < request.dist or dist < (grant.dist + request.dist)):
                        grant.status = "TERMINATED"
                        for i, item in enumerate(SpectrumList):
                            if(item['cbsdId'] == grant.cbsdId):
                                item['state'] = 1
                                item['stateText'] = "Registered"
                                SpectrumList[i] = item
                        for i, cbsd in enumerate(CbsdList):
                            if(cbsd['cbsdId'] == grant.cbsdId):
                                cbsd['state'] = 1
                                cbsd['stateText'] = "Registered"
                                CbsdList[i] = cbsd
                        socket.emit('spectrumUpdate', SpectrumList)
                        socket.emit('cbsdUpdate', CbsdList)
                        time.sleep(1)
                else:
                    if(dist < (grant.dist + request.dist)):
                        conflict = True
                    else:
                        print("Distance greater than threshold")

        if conflict == True:
            print("Conflict detected")
            delattr(gr, 'grantExpireTime')
            delattr(gr, 'heartbeatInterval')
            delattr(gr, 'measReportConfig')
            delattr(gr, 'grantId')
            delattr(gr, 'channelType')
            gr.response = self.generateResponse(401)
            print(gr.response)
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
        # Return 0 = not present, 1 = present, 2 = no spectrum data, 3 = error with alorithm select
        latit = self.latitude
        longit = self.longitude
        rad = self.radius
        if latitude != None and longitude != None:
            longit = longitude
            latit = latitude
        if radius != None:
            rad = radius
        remData = REM.getSpectrumDataWithParameters(longit, latit, highFreq, lowFreq, rad)  # GET ALL  REM DATA
        if not remData:
            # print("Currently no spectrum data") # TODO: remove comment
            return 2
            # self.setREMAlgorithm('DEFAULT')
        if self.getREMAlgorithm() == 'DEFAULT':
            if self.defaultREMAlgorithm(remData):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'TRUSTSCORE':
            if self.trustScoreREMAlgorithm(remData):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'TSRL':
            if self.trustScoreRemoveLowestREMAlgorithm(remData):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'SECREM':
            if self.secREMAlgorithm(remData):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'SECREMCELLS':
            if self.secREMAlgorithmWithCells(remData, REM):
                return 1
            else:
                return 0
        elif self.getREMAlgorithm() == 'NOFK':
            if self.nofkREMAlgorithm(remData):
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

    def calculateGrantExpireTime(self, grants, REM, grant, renew, request=None):
        grantCount = len(grants)
        t = datetime.now(timezone.utc) if not request else datetime.fromisoformat(request.vtGrantParams.startTime)
        if grantCount <= 1:
            t = t + timedelta(seconds=self.maxGrantTime)
            return t.strftime(self.DEFAULT_TIME_FORMAT)
        else:
            t = t + timedelta(seconds=(self.defaultHeartbeatInterval * 2))
            return t.strftime(self.DEFAULT_TIME_FORMAT)

    def getHighFreqFromOP(self, params):
        return params.operationFrequencyRange.highFrequency

    def getLowFreqFromOP(self, params):
        return params.operationFrequencyRange.lowFrequency

    def frequencyOverlap(self, freqa, freqb, rangea, rangeb):
        if (freqa <= rangea and freqb >= rangea):
            return True
        elif (freqa >= rangea and freqb <= rangeb):
            return True
        elif (freqa <= rangeb and freqb >= rangeb):
            return True
        elif (freqa <= rangea and freqb >= rangeb):
            return True
        else:
            return False

    def defaultREMAlgorithm(self, remData):
        total = 0.0
        # Equal weight with threshold parameter, no location, all parameters
        if remData:
            for data_point in remData:
                total = total + float(data_point.powerLevel)
            if (total * 1.0 / len(remData)) > self.threshold:
                return True
        return False

    def nofkREMAlgorithm(self, remData):
        yes = 0
        no = 0
        # Equal weight with threshold parameter, no location, all parameters
        for data_point in remData:
            if data_point.powerLevel >= self.threshold:
                yes = yes + 1
            else:
                no = no + 1

        if yes > no:
            return True
        else:
            return False

    def trustScoreREMAlgorithm(self, remData):
        # Trust scores with threshold parameter, no location, all parameters
        totalTandP = 0.0
        totalTrustLevel = 0
        for data_point in remData:
            totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
            totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
        if totalTandP > (self.threshold * totalTrustLevel):
            return True
        else:
            return False

    def secREMAlgorithm(self, remData):
        # Trust scores with threshold parameter, no location, all parameters
        totalTandP = 0.0
        totalTrustLevel = 0.0
        variance = self.getVarianceOfData(remData)
        for data_point in remData:
            if (variance > 600 and data_point.cbsd.fullyTrusted):
                totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
            else:
                totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
            if (variance > 200 and data_point.cbsd.fullyTrusted):  # double count secure nodes
                totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
        if totalTandP > (self.threshold * totalTrustLevel):
            return True
        else:
            return False

    def getVarianceOfData(self, remData):
        dataForVar = []
        for data in remData:
            dataForVar.append(data.powerLevel)
        return numpy.var(dataForVar)

    def trustScoreRemoveLowestREMAlgorithm(self, remData):
        # Trust scores with threshold parameter, no location, all parameters
        totalTandP = 0.0
        totalTrustLevel = 0.0
        choppedRemData = self.removeDataWithLowestTrustScores(5, remData)
        for data_point in choppedRemData:
            totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
            totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
        if totalTandP > (self.threshold * totalTrustLevel):
            return True
        else:
            return False

    def removeDataWithLowestTrustScores(self, percentRemoved, remData):
        cbsds = []
        for data_point in remData:
            if data_point.cbsd not in cbsds:
                cbsds.append(data_point.cbsd)
        removeCount = max(1, (float(percentRemoved) / 100.0) * len(cbsds))
        removeCount = int(removeCount)  # make whole number
        if len(cbsds) < 5:  # if there are less than 5 cbsds
            return remData
        lowestTrustNodes = []

        for x in range(5, 40):
            if len(lowestTrustNodes) < removeCount:
                for cbsd in cbsds:
                    if (cbsd.trustLevel == x / 10.0):
                        lowestTrustNodes.append(cbsd)
                        cbsds.remove(cbsd)

        for data in remData:
            if data.cbsd in lowestTrustNodes:
                remData.remove(data)
        return remData

    def secREMAlgorithmWithCells(self, remData, REM):
        # Trust scores with threshold parameter, no location, all parameters
        totalTandP = 0.0
        totalTrustLevel = 0.0
        variance = self.getVarianceOfData(remData)
        for x in REM.cells:  # clear data
            x.data = []

        for d in remData:  # put each data point into its cell or cells
            for cell in REM.cells:
                if cell.isInCell(d):
                    cell.data.append(d)

        for c in REM.cells:  # calculate the variance of each cell
            c.variance = self.getVarianceOfData(c.data)
        if len(REM.cells) > 1:
            worst = 0
            worstId = -1
            best = 1000000
            bestId = -1
            for cell in REM.cells:
                if cell.variance and len(cell.data) > 1:
                    if cell.variance < best:
                        best = cell.variance
                        bestId = cell.id
                    if cell.variance > worst:
                        worst = cell.variance
                        worstId = cell.id

            for cellCheck in REM.cells:
                if cellCheck.id == worstId and cellCheck.id == bestId:
                    cellCheck.worst = False
                    cellCheck.best = False
                elif cellCheck.id == worstId:
                    cellCheck.worst = True
                    cellCheck.best = False
                else:
                    cellCheck.worst = False
                    cellCheck.best = True

        for cell in REM.cells:
            for data_point in cell.data:
                if (variance > 6000 and data_point.cbsd.fullyTrusted):  # system variance
                    totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                    totalTrustLevel = totalTrustLevel + (data_point.cbsd.trustLevel)
                elif data_point.cbsd.fullyTrusted:
                    totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                    totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
                else:
                    if cell.worst:
                        totalTandP = totalTandP + 0.9 * (data_point.cbsd.trustLevel * data_point.powerLevel)
                        totalTrustLevel = totalTrustLevel + 0.9 * data_point.cbsd.trustLevel
                    elif cell.best:
                        totalTandP = totalTandP + 1.1 * (data_point.cbsd.trustLevel * data_point.powerLevel)
                        totalTrustLevel = totalTrustLevel + 1.1 * data_point.cbsd.trustLevel
                    else:
                        totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                        totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel

                if (cell.variance > 200 and data_point.cbsd.fullyTrusted):  # double count secure nodes
                    totalTandP = totalTandP + (data_point.cbsd.trustLevel * data_point.powerLevel)
                    totalTrustLevel = totalTrustLevel + data_point.cbsd.trustLevel
        if totalTandP > (self.threshold * totalTrustLevel):
            return True
        else:
            return False

    def trustedREMAlgorithm(self, remData):
        # Only use if trust score is high enough
        # Trust scores with threshold parameter, no location, all parameters
        count = 0
        total = 0.0
        trustCutoff = 7.0  # don't count if less than score
        for data_point in remData:
            if data_point.cbsd.trustScore > trustCutoff:
                total = total + float(data_point.powerLevel)
                count = count + 1
        if (total * 1.0 / count) > self.threshold:
            return True
        else:
            return False

    def acceptableRange(self, lowFreq, highFreq):
        return (lowFreq < highFreq) and (lowFreq >= self.MINCBRSFREQ) and (highFreq <= self.MAXCBRSFREQ)

    def acceptableBandwidth(self, lowFreq, highFreq):
        return self.minimumGrantSize <= highFreq - lowFreq <= self.maximumGrantSize and lowFreq % 5 == 0 and \
               highFreq % 5 == 0

    def createDPAGrant(self, dpa, grants, CbsdList, SpectrumList):
        grantResponse = WinnForum.GrantResponse()
        grantRequest = WinnForum.GrantRequest(dpa["id"], None)
        ofr = WinnForum.FrequencyRange(dpa["spectrum"][0][0], dpa["spectrum"][0][1])
        op = WinnForum.OperationParam(30, ofr)
        grantRequest.operationParam = op
        # request = { "cbsdId" : dpa["id"], "operationParam": { "operationFrequencyRange": { "lowFrequency": dpa["spectrum"][0][0], "highFrequency": dpa["spectrum"][0][1] } } }
        grantRequest.lat = dpa["latitude"]
        grantRequest.long = dpa["longitude"]
        grantRequest.IsDPA = True
        grantRequest.dist = dpa["radius"]
        grantResponse = self.defaultGrantAlg(grants, None, grantRequest)
        g = WinnForum.Grant(grantResponse.grantId, dpa["id"], grantResponse.operationParam, None,
                            grantResponse.grantExpireTime)
        g.IsDpa = True
        g.lat = dpa["latitude"]
        g.long = dpa["longitude"]
        g.id = dpa["id"]
        g.dist = dpa["radius"]
        return g

    def calculateDistance(self, a, b):
        lat1, lon1 = a
        lat2, lon2 = b
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d