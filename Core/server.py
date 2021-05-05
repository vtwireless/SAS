import eventlet #pip install eventlet
import socketio #pip install socketio
import requests
import json
import SASAlgorithms
import SASREM
import time
from datetime import datetime, timedelta, timezone
import WinnForum
import CBSD
import threading
import uuid

GETURL = "http://localhost/SASAPI/SAS_API_GET.php"
POSTURL = "http://localhost/SASAPI/SAS_API.php"
SASKEY = "qowpe029348fuqw9eufhalksdjfpq3948fy0q98ghefqi"

allClients = []
allRadios = [] #CBSDSocket
allWebApps = []
allSASs = []
grants = []
cbsds = [] #cbsd references


databaseLogging = False
josephsMac = False # timezone isnt cooperating on Mac

socket = socketio.Server()
app = socketio.WSGIApp(socket, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()
NUM_OF_CHANNELS = int((SASAlgorithms.MAXCBRSFREQ - SASAlgorithms.MINCBRSFREQ)/SASAlgorithms.TENMHZ)

def sendGetRequest(parameters):
    parameters["SAS_KEY"] = SASKEY
    x = requests.post(GETURL, parameters)
    return x.json()


def generateResponse(responseCode):
    response = {}
    response["responseCode"] = str(responseCode)
    response["message"] = WinnForum.responseDecode(responseCode)
    return response

def sendPostRequest(parameters):
    parameters["SAS_KEY"] = SASKEY
    x = requests.post(POSTURL, parameters)
    print(x.text)
    return x.json()

def getSettings() :
    if databaseLogging:
        getAl = { "action": "getSettings"}
        result = sendGetRequest(getAl)
        SASAlgorithms.setGrantAlgorithm(result["algorithm"])
        SASAlgorithms.setHeartbeatInterval(result["heartbeatInterval"])
        SASAlgorithms.setREMAlgorithm(result["REMAlgorithm"])
    else:
        SASAlgorithms.setGrantAlgorithm('DEFAULT')
        SASAlgorithms.setHeartbeatInterval(5)
        SASAlgorithms.setREMAlgorithm('DEFAULT')
    print('GRANT: ' + SASAlgorithms.getGrantAlgorithm() + ' HB: ' + str(SASAlgorithms.getHeartbeatInterval()) + ' REM: ' + SASAlgorithms.getREMAlgorithm())

def sendBroadcast(broadcastName, data):
    socket.emit(broadcastName, data)

#def addObjectToREM(spectrumData):
#     obj = SASREM.SASREMObject(5, 50, "obj", 5, 3500000, 3550000, time.time() )
#    REM.addREMObject(obj)

def getGrantWithID(grantId):
    for grant in grants:
        if str(grant.id) == str(grantId):
            return grant
    if databaseLogging:
        param = { "action": "getGrant", "grantId": grantId }
        res = sendGetRequest(param)
        if res["status"]=="1":
            return loadGrantFromJSON(res["grant"])
        else:
            print("false GrantId")
            return None  
    else:
        return None

def loadGrantFromJSON(json_file):
    ofr = WinnForum.FrequencyRange(json_file["frequency"], json_file["frequency"] + json_file["bandwidth"])
    operationParam = WinnForum.OperationParam(json_file["requestPowerLevel"], ofr)
    vtgp = WinnForum.VTGrantParams(None, None, None, None, None, None, None, None,None, None, None, None, None, None, None)
    try:
        vtgp.minFrequency = json_file["requestMinFrequency"]
        vtgp.maxFrequency = json_file["requestMaxFrequency"]
        vtgp.startTime = json_file["startTime"]
        vtgp.endTime = json_file["endTime"]
        vtgp.approximateByteSize = json_file["requestApproximateByteSize"]
        vtgp.dataType = json_file["dataType"]
        vtgp.powerLevel = json_file["requestPowerLevel"]
        vtgp.location = json_file["requestLocation"]
        vtgp.mobility = json_file["requestMobility"]
        vtgp.maxVelocity = json_file["requestMaxVelocity"]
    except KeyError:
        print("No vtparams")
    grant = WinnForum.Grant(json_file["grantID"], json_file["secondaryUserID"], operationParam, vtgp)
    grants.append(grant)
    return grant 

def generateId():
    return str(uuid.uuid4())#time.time()#just generate using epoch time, not really that important, but is unique

def getCBSDWithId(cbsdId):
    for cbsd in cbsds:
        if str(cbsd.id) == str(cbsdId):
            return cbsd
    if databaseLogging:
        param = { "action": "getNode", "nodeId": cbsdId }
        res = sendGetRequest(param)
        if res["status"]=="1":
            return loadCBSDFromJSON(res["node"])
        else:
            print("false CBSDId")
            return None  
    else:
        return None 
    
def loadCBSDFromJSON(json):
    locArr = json["location"].split(",")
    longitude = locArr[0]
    latitude = locArr[0]

    cbsd = CBSD.CBSD(json["id"], json["trustLevel"], json["fccId"], json["name"], longitude, latitude, \
        json["IPAddress"], json["minFrequency"], json["maxFrequency"], json["minSampleRate"], \
            json["maxSampleRate"], json["cbsdType"], json["mobility"], json["status"], \
                json["cbsdSerialNumber"], json["callSign"], json["cbsdCategory"], json["cbsdInfo"], json["airInterface"],\
                    json["installationParam"], json["measCapability"], json["groupingParam"])
    allClients.append(cbsd)
    return cbsd

def measReportObjectFromJSON(json):
    return WinnForum.RcvdPowerMeasReport(json["measFrequency"], json["measBandwidth"], json["measRcvdPower"] or 0)

def removeGrant(grantId, cbsdId):
    for g in grants:
        if str(g.id) == str(grantId) and str(g.cbsdId) == str(cbsdId):
            grants.remove(g)
            return True
    return False

def removeCBSD(cbsdId):
    for c in cbsds:
        if (c.id) == str(cbsdId):
            cbsds.remove(c)
            return True
    return False
            

@socket.event
def connect(sid, environ):
    print('connect ', sid)
    allClients.append(sid)

# @socket.event
# def my_message(sid, data):
#     print('message ', data)

@socket.event
def disconnect(sid):
    print('disconnect ', sid)
    allClients.remove(sid)
    if sid in allWebApps: allWebApps.remove(sid)
    if sid in allSASs: allSASs.remove(sid)
    for radio in allRadios:
        if radio.sid == sid:
            allRadios.remove(radio)

@socket.on('registrationRequest')
def register(sid, data):
    jsonData = json.loads(data)
    responseArr = []
    assignmentArr = []
    for item in jsonData["registrationRequest"]:
        radio = CBSD.CBSD('0', 5, item["fccId"])
        if "vtParams" in item:
            item["nodeType"] = item["vtParams"]["nodeType"]
            item["minFrequency"] = item["vtParams"]["minFrequency"]
            item["maxFrequency"] = item["vtParams"]["maxFrequency"]
            item["minSampleRate"] = item["vtParams"]["minSampleRate"]
            item["maxSampleRate"] = item["vtParams"]["maxSampleRate"]
            item["mobility"] = item["vtParams"]["isMobile"]

            radio.nodeType = item["vtParams"]["nodeType"]
            radio.minFrequency = item["vtParams"]["minFrequency"]
            radio.maxFrequency = item["vtParams"]["maxFrequency"]
            radio.minSampleRate = item["vtParams"]["minSampleRate"]
            radio.maxSampleRate = item["vtParams"]["maxSampleRate"]
            radio.mobility = item["vtParams"]["isMobile"]
        if "installationParam" in item:
            if "latitude" in item["installationParam"] and "longitude" in item["installationParam"]:
                item["location"] = str(item["installationParam"]["latitude"]) + ',' + str(item["installationParam"]["longitude"])
                radio.latitude = item["installationParam"]["latitude"]
                radio.longitude = item["installationParam"]["longitude"]
        item["IPAddress"] = 'TODO IP'
        item["action"] = "createNode"
        if databaseLogging:
            print(sendPostRequest(item))
            radio.id = 'TODO'
        else:
            radio.id = generateId()
            allClients.append(radio)
            cbsds.append(radio)
        if "measCapability" in item:#if the registering entity is a radio add it to the array and give it an assignment
            cbsd = SASREM.CBSDSocket(radio.id, sid, False)
            assignmentArr.append(cbsd)
        response = WinnForum.RegistrationResponse(radio.id, None, SASAlgorithms.generateResponse(0))
        if "measCapability" in item:
            response.measReportConfig = item["measCapability"]
        responseArr.append(response.asdict())
    responseDict = {"registrationResponse":responseArr}
    print(responseDict)
    socket.emit('registrationResponse', to=sid, data=json.dumps(responseDict))
    #if the radio does not get the assignment out of the meas config
    for radio in assignmentArr:
        sendAssignmentToRadio(radio)

@socket.on('deregistrationRequest')
def deregister(sid, data):
    jsonData = json.loads(data)
    responseArr = []
    for item in jsonData["deregistrationRequest"]:
        if databaseLogging:
            item["action"] = "deregisterNode"
            print(sendPostRequest(item))
            response = {}
            response["cbsdId"] = item["cbsdId"]
            response["response"] = generateResponse(0)
            responseArr.append(response) #TODO
        success = removeCBSD(item["cbsdId"])
        response = WinnForum.DeregistrationResponse()
        if success:
            response.cbsdId = item["cbsdId"]
            response.response = SASAlgorithms.generateResponse(0)
        else:
            response.cbsdId = item["cbsdId"]
            response.response = SASAlgorithms.generateResponse(103)
        responseArr.append(response.asdict())
    responseDict = {"deregistrationResponse":responseArr}
    socket.emit('deregistrationResponse', to=sid, data=json.dumps(responseDict))   

@socket.on('grantRequest')
def grantRequest(sid, data):
    jsonData = json.loads(data)
    print(jsonData)
    responseArr = []
    for item in jsonData["grantRequest"]:
        item["secondaryUserID"] = item["cbsdId"]
        if "operationParam" in item:
            item["powerLevel"] = item["operationParam"]["maxEirp"]
            item["minFrequency"] = int(item["operationParam"]["operationFrequencyRange"]["lowFrequency"])
            item["maxFrequency"] = int(item["operationParam"]["operationFrequencyRange"]["highFrequency"])
        if "vtGrantParams" in item:
            item["approximateByteSize"] = int(item["vtGrantParams"]["approximateByteSize"])
            item["dataType"] = item["vtGrantParams"]["dataType"]
            item["mobility"] = item["vtGrantParams"]["mobility"]
            item["maxVelocity"] = item["vtGrantParams"]["maxVelocity"]
            item["preferredFrequency"] = int(item["vtGrantParams"]["preferredFrequency"])
            item["preferredBandwidth"] = int(item["vtGrantParams"]["preferredBandwidth"])
            item["minBandwidth"] = int(item["vtGrantParams"]["minBandwidth"])
            item["frequencyAbsolute"] = int(item["vtGrantParams"]["frequencyAbsolute"])
            item["dataType"] = item["vtGrantParams"]["dataType"]
            item["startTime"] = item["vtGrantParams"]["startTime"]
            item["endTime"] = item["vtGrantParams"]["endTime"]
            item["location"] = item["vtGrantParams"]["location"]
        item["action"] = "createGrantRequest"
        grantRequest = WinnForum.GrantRequest(item["cbsdId"], None)
        if "operationParam" in item:
            ofr = WinnForum.FrequencyRange(item["minFrequency"], item["maxFrequency"])
            op = WinnForum.OperationParam(item["powerLevel"], ofr)
            grantRequest.operationParam = op
        vtgp = None
        if "vtGrantParams" in item:
            vt = item["vtGrantParams"]
            vtgp = WinnForum.VTGrantParams(None, None, vt["preferredFrequency"], vt["frequencyAbsolute"], vt["minBandwidth"], vt["preferredBandwidth"], vt["preferredBandwidth"], vt["startTime"], vt["endTime"], vt["approximateByteSize"], vt["dataType"], vt["powerLevel"], vt["location"], vt["mobility"], vt["maxVelocity"])
            grantRequest.vtGrantParams = vtgp
        grantResponse = SASAlgorithms.runGrantAlgorithm(grants, REM, grantRequest)#algorithm   
        if databaseLogging:
            sendPostRequest(item)#Database log
        else:
            grantResponse.grantId = generateId()
        if grantResponse.response.responseCode == "0":
            g = WinnForum.Grant(grantResponse.grantId, item["cbsdId"], grantResponse.operationParam, vtgp, grantResponse.grantExpireTime)
            grants.append(g)
        responseArr.append(grantResponse.asdict())
    responseDict = {"grantResponse":responseArr}
    socket.emit('grantResponse', to=sid, data=json.dumps(responseDict))

@socket.on('heartbeatRequest')
def heartbeat(sid, data):
    jsonData = json.loads(data)
    hbrArray = []
    grantArray = []
    for hb in jsonData["heartbeatRequest"]:
        cbsd = getCBSDWithId(hb["cbsdId"])
        grant = getGrantWithID(hb["grantId"])
        grantArray.append(grant)
        try:
            if hb["measReport"]:
                for rpmr in hb["measReport"]["rcvdPowerMeasReports"]:
                    #Future TODO: check to see if frequency range already exists as a submission from specific CBSD to prevent spamming
                    mr = measReportObjectFromJSON(rpmr)#this should be an array
                    REM.measReportToSASREMObject(mr, cbsd)
        except KeyError:
            print("no measure report")
        response = SASAlgorithms.runHeartbeatAlgorithm(grants, REM, hb, grant)
        if(josephsMac):
            grant.heartbeatTime = datetime.now(time.timezone.utc)
        else:
            grant.heartbeatTime = datetime.now(timezone.utc)
        grant.heartbeatInterval = response.heartbeatInterval
        hbrArray.append(response.asdict())
    responseDict = {"heartbeatResponse":hbrArray}
    socket.emit('heartbeatResponse', to=sid, data=json.dumps(responseDict))

    for g in grantArray:
        threading.Timer((response.heartbeatInterval*1.1)+2, cancelGrant, [g]).start()

@socket.on('relinquishmentRequest')
def relinquishment(sid, data):
    jsonData = json.loads(data)
    relinquishArr = []
    for relinquishmentRequest in jsonData["relinquishmentRequest"]:
        params = {}
        params["cbsdId"] = relinquishmentRequest["cbsdId"]
        params["grantId"] = relinquishmentRequest["grantId"]
        params["action"] = "relinquishGrant"
        if databaseLogging:
            sendPostRequest(params)
        success = removeGrant(getGrantWithID(relinquishmentRequest["grantId"]).id, relinquishmentRequest["cbsdId"])
        response = {}
        response["cbsdId"] = relinquishmentRequest["cbsdId"]
        response["grantId"] = relinquishmentRequest["grantId"]
        if relinquishmentRequest["cbsdId"] == None or relinquishmentRequest["grantId"] == None:
            response["response"] = generateResponse(102)
        elif success:
            response["response"] = generateResponse(0) 
        else:
            response["response"] = generateResponse(103) 
        relinquishArr.append(response)
    responseDict = {"relinquishmentResponse":relinquishArr}
    socket.emit('relinquishmentResponse', to=sid, data=json.dumps(responseDict))

@socket.on('spectrumInquiryRequest')
def spectrumInquiryRequest(sid, data):
    jsonData = json.loads(data)
    inquiryArr = []
    for request in jsonData["spectrumInquiryRequest"]:
        response = WinnForum.SpectrumInquiryResponse(request["cbsdId"], [], SASAlgorithms.generateResponse(0))
        for fr in request["inquiredSpectrum"]:
            lowFreq = int(fr["lowFrequency"])
            highFreq = int(fr["highFrequency"])
            channelType = "PAL"
            ruleApplied = "FCC_PART_96"
            maxEirp = SASAlgorithms.getMaxEIRP()
            if SASAlgorithms.acceptableRange(lowFreq, highFreq):
                if highFreq < 3700000000 and highFreq > 3650000000:
                    channelType = "GAA"
                present = SASAlgorithms.isPUPresentREM(REM, highFreq, lowFreq, None, None, None)
                if present == 0:#not present
                    fr = WinnForum.FrequencyRange(lowFreq, highFreq)
                    availChan = WinnForum.AvailableChannel(fr, channelType, ruleApplied, maxEirp)
                    response.availableChannel.append(availChan)
                elif present == 2:#no spectrum data
                    initiateSensing(lowFreq, highFreq)


        inquiryArr.append(response.asdict())
    responseDict = {"spectrumInquiryResponse":inquiryArr}
    socket.emit('spectrumInquiryResponse', to=sid, data=json.dumps(responseDict))

@socket.on('changeSettings')
def changeAlgorithm(sid, data):
    getSettings()

@socket.on('spectrumData')
def spectrumData(sid, data):
    jsonData = json.loads(data)
    print(jsonData) #TODO Remove
    cbsd = None
    try:
        cbsd = getCBSDWithId(jsonData["spectrumData"]["cbsdId"])
    except KeyError:
        pass
    try:
        if jsonData["spectrumData"]["spectrumData"]:
            for rpmr in jsonData["spectrumData"]["spectrumData"]["rcvdPowerMeasReports"]:
                mr = measReportObjectFromJSON(rpmr)
                REM.measReportToSASREMObject(mr, cbsd)
    except KeyError:
        print("rcvd power meas error")

@socket.on('incumbentInformation')
def incumbentInformation(sid, data):
    """Function for PUs to send their operating data"""
    utilizeExtraChannel = True # TODO: Decide when to toggle this
    jsonData = json.loads(data)
    for data in jsonData["incumbentInformation"]:
        # Get time, location, and frequency range of PU
        desireObfuscation = None
        startTime = None
        puLat = None
        puLon = None
        puLowFreq = None
        puLighFreq = None
        power = None
        try:
            desireObfuscation = bool(data["desireObfuscation"])
            puLowFreq = float(data["lowFreq"])
            puHighFreq = float(data["highFreq"])
        except KeyError as ke:
            print("error in unpacking PU data")
            print(ke)
        try:
            puLat = data["puLat"]
            puLon = data["puLon"]
            power = data["power"]
            startTime = data["startTime"]
        except:
            pass
        if(desireObfuscation):
            if(utilizeExtraChannel):
                #Find the channel where the lowest PU frequency resides
                puLowChannel = getChannelFromFrequency(puLowFreq)
                channelFreqLow = getChannelFreqFromChannel(puLowChannel)
                lowCbsdBw = puLowFreq - channelFreqLow

                #Find the channel where the highest PU frequency resides
                puHighChannel = getChannelFromFrequency(puHighFreq)
                channelFreqHigh = getChannelFreqFromChannel(puHighChannel, getHighFreq=True)
                highCbsdBw = channelFreqHigh - puHighFreq

                # If there is as least 1kHz between a channel and the PU, turn on an adjacent CBSD
                if(lowCbsdBw > 1000):
                    # sendIICCommand(channelFreqLow, puLowFreq) # TODO
                    sendIICCommand(puLowFreq-1e6, puLowFreq)
                if(highCbsdBw > 1000):
                    sendIICCommand(puHighFreq, channelFreqHigh)
            else:
                pass # Do not want to use an extra channel
        else:
            pass # PU does not want special treatment

def getChannelFreqFromChannel(channel, getHighFreq=False):
    """Convert a channel integer to a freq for the channel"""
    if(getHighFreq):
        channel = channel + 1
    return (channel*SASAlgorithms.TENMHZ)+SASAlgorithms.MINCBRSFREQ
        

def getChannelFromFrequency(freq):
    """Returns the lowFreq for the channel 'freq' can be found"""
    for channel in range(NUM_OF_CHANNELS):
        if(freq < ((channel+1)*SASAlgorithms.TENMHZ)+SASAlgorithms.MINCBRSFREQ):
            return channel
    return None

def initiateSensing(lowFreq, highFreq):
    count = 0
    radioCountLimit = 3
    radiosToChangeBack = []
    #loop through radios, set 3 as the limit
    for radio in allRadios:
        if not radio.justChangedParams:
            changeParams = dict()
            changeParams["lowFrequency"] = lowFreq
            changeParams["highFrequency"] = highFreq
            changeParams["cbsdId"] = radio.cbsdId
            radio.justChangedParams = True
            socket.emit("changeRadioParams", data=changeParams, room=radio.sid)
            radiosToChangeBack.append(radio)
            count = count + 1
        if count >= radioCountLimit or count > len(allRadios)/3:
        #don't use more than 1/3 of the radios to check band
            break
    
    threading.Timer(3.0, resetRadioStatuses, [radiosToChangeBack]).start()

def resetRadioStatuses(radios):
    for radio in radios:
        radio.justChangedParams = False

def cancelGrant(grant):
    if(josephsMac):
        now = datetime.now(time.timezone.utc)
    else:
        now = datetime.now(timezone.utc)
    if grant.heartbeatTime + timedelta(0, grant.heartbeatInterval) < now:
        removeGrant(grant.id, grant.cbsdId)
        print('grant ' + grant.id + ' canceled')

def singleFrequencyOverlap(self, freq, lowFreq, highFreq):
    """Checks to see if freq is within range"""
    if (freqa <= highFreq and freqb >= lowFreq):
        return True
    else:
        return False

def sendAssignmentToRadio(cbsd):
    print("a sensing radio has joined")
    if cbsd in allRadios:
        allRadios.remove(cbsd)
    allRadios.append(cbsd)
    freqRange = SASAlgorithms.MAXCBRSFREQ - SASAlgorithms.MINCBRSFREQ # 3.5 GHz CBRS Band is 150 MHz wide
    blocks = freqRange/SASAlgorithms.TENMHZ
    for i in range(int(blocks)):
        low = (i * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        high = ((i + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        result = SASAlgorithms.isPUPresentREM(REM, low, high, None, None, None)
        if result == 2:
            #if there is no spectrum data available for that frequency range assign radio to it
            changeParams = dict()
            changeParams["lowFrequency"] = str((SASAlgorithms.TENMHZ * i) + SASAlgorithms.MINCBRSFREQ)
            changeParams["highFrequency"] =str((SASAlgorithms.TENMHZ * (i+ 1)) + SASAlgorithms.MINCBRSFREQ)
            changeParams["cbsdId"] = cbsd.cbsdId
            cbsd.justChangedParams = True
            socket.emit("changeRadioParams", to=cbsd.sid, data=changeParams)
            break
    
    threading.Timer(3.0, resetRadioStatuses, [[cbsd]]).start()

def sendIICCommand(lowFreq, highFreq):
    """Will ask 1 idle node to transmit over the low-high freq"""
    radioCountLimit = 1
    radiosToChangeBack = []
    global allRadios
    for radio in allRadios:  
        if not radio.justChangedParams:
            print("SENDING LOW: " +str(lowFreq)+" and HIGH: "+str(highFreq))
            sendObstructionToRadio(radio, lowFreq, highFreq)
            radiosToChangeBack.append(radio)
            threading.Timer(3.0, resetRadioStatuses, [radiosToChangeBack]).start()
            return True
    return False


def obstructChannel(lowFreq, highFreq, latitude, longitude):
    print("NGGYU")
    result = SASAlgorithms.isPUPresentREM(REM, lowFreq, highFreq, latitude, longitude, None)
    if result == 0:
        count = 0
        latLongThresh = 2
        radioCountLimit = 3
        radiosToChangeBack = []
        if not latitude and not longitude:    
            #loop through radios, set 3 as the limit
            for radio in allRadios:  
                if not radio.justChangedParams:
                    sendObstructionToRadio(radio, lowFreq, highFreq)
                    radiosToChangeBack.append(radio)
                    count = count + 1
                if count >= radioCountLimit or count > len(allRadios)/3:
                #don't use more than 1/3 of the radios to check band
                    break
        else:
            for cbsd in cbsds:
                if cbsd.latitude and cbsd.longitude:
                    if abs(cbsd.latitude - latitude) < latLongThresh and abs(cbsd.longitude - longitude):
                        for radio in allRadios:  
                            if not radio.justChangedParams and cbsd.id == radio.id:
                                sendObstructionToRadio(radio, lowFreq, highFreq)
                                radiosToChangeBack.append(radio)
                                count = count + 1
                            if count >= radioCountLimit or count > len(allRadios)/3:
                            #don't use more than 1/3 of the radios to check band
                                break 
        threading.Timer(3.0, resetRadioStatuses, [radiosToChangeBack]).start()


def sendObstructionToRadio(cbsd, lowFreq, highFreq):
    changeParams = dict()
    changeParams["lowFrequency"] = lowFreq
    changeParams["highFrequency"] = highFreq
    changeParams["cbsdId"] = cbsd.cbsdId
    cbsd.justChangedParams = True
    socket.emit("obstructChannelWithRadioParams", json.dumps(changeParams), to=cbsd.sid)

def checkPUAlert():
    freqRange = SASAlgorithms.MAXCBRSFREQ - SASAlgorithms.MINCBRSFREQ
    blocks = freqRange/SASAlgorithms.TENMHZ
    for i in range(int(blocks)):
        low = (i * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        high = ((i + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        result = SASAlgorithms.isPUPresentREM(REM, low, high, None, None, None)
        if result == 1:
            for grant in grants:
                if SASAlgorithms.frequencyOverlap(low, high, SASAlgorithms.getLowFreqFromOP(grant.operationParam), SASAlgorithms.getHighFreqFromOP(grant.operationPARAM)):
                    cbsd = getCBSDWithId(grant.cbsdId)
                    cbsd.sid.emit('pauseGrant', { 'grantId' : grant.id })
    
    threading.Timer(1.5, checkPUAlert).start()
   

if __name__ == '__main__':
    getSettings()
    threading.Timer(3.0, checkPUAlert).start()
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

