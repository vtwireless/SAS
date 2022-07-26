"""
Very similar to server.py

Revised: March 20, 2021
Authored by: Cameron Makin (cammakin8@vt.edu), Joseph Tolley (jtolley@vt.edu)
Advised by Dr. Carl Dietrich (cdietric@vt.edu)
For Wireless@VT
"""

import eventlet
import socketio
import requests
import json
import threading
import uuid
import random
import sqlalchemy
import time
from datetime import datetime, timedelta, timezone

import SASAlgorithms
import SASREM
import Server_WinnForum as WinnForum
import CBSD
import DatabaseController

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
isSimulating = True
NUM_OF_CHANNELS = 15
puDetections = {}

socket = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(socket, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})
db = DatabaseController.DatabaseController()

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()

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

def getSettings():
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

def loadGrantFromJSON(json):
    ofr = WinnForum.FrequencyRange(json["frequency"], json["frequency"] + json["bandwidth"])
    operationParam = WinnForum.OperationParam(json["requestPowerLevel"], ofr)
    vtgp = WinnForum.VTGrantParams(None, None, None, None, None, None, None, None,None, None, None, None, None, None, None)
    try:
        vtgp.minFrequency = json["requestMinFrequency"]
        vtgp.maxFrequency = json["requestMaxFrequency"]
        vtgp.startTime = json["startTime"]
        vtgp.endTime = json["endTime"]
        vtgp.approximateByteSize = json["requestApproximateByteSize"]
        vtgp.dataType = json["dataType"]
        vtgp.powerLevel = json["requestPowerLevel"]
        vtgp.location = json["requestLocation"]
        vtgp.mobility = json["requestMobility"]
        vtgp.maxVelocity = json["requestMaxVelocity"]
    except KeyError:
        print("No vtparams")
    grant = WinnForum.Grant(json["grantID"], json["secondaryUserID"], operationParam, vtgp)
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
    return WinnForum.RcvdPowerMeasReport(float(json["measFrequency"]), json["measBandwidth"], json["measRcvdPower"] or 0)

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

# In[ --- Connection Management ---]

@socket.event
def connect(sid, environ):
    print('connect ', sid)
    allClients.append(sid)

@socket.event
def disconnect(sid):
    print('disconnect ', sid)
    allClients.remove(sid)
    if sid in allWebApps: allWebApps.remove(sid)
    if sid in allSASs: allSASs.remove(sid)
    for radio in allRadios:
        if radio.sid == sid:
            allRadios.remove(radio)

# In[ --- User Management ---]

@socket.on('suLogin')
def suLogin(sid, data):
    response = db.authenticate_user(data, False)
    socket.emit('suLoginResponse', to=sid, data=response)

    # socket.disconnect(sid)

@socket.on('adminLogin')
def adminLogin(sid, data):
    response = db.authenticate_user(data, True)
    socket.emit('adminLoginResponse', to=sid, data=response)

    # socket.disconnect(sid)

@socket.on('createSU')
def createSecondaryUser(sid, data):
    response = db.create_user(data, False)
    socket.emit('createSUResponse', to=sid, data=response)

    # socket.disconnect(sid)

@socket.on('createAdminUserINsas')
def createAdminUser(sid, data):
    response = db.create_user(data, True)
    socket.emit('createAdminUserINsasResponse', to=sid, data=response)

    # socket.disconnect(sid)

# In[ --- Node Management ---]

@socket.on('getNodesRequest')
def getNodes(sid, payload):
    response = db.get_nodes()
    socket.emit('getNodesResponse', to=sid, data=response)

@socket.on('registrationRequest')
def register(sid, nodes):
    response, assignmentArr = db.create_nodes(sid, nodes)
    socket.emit('registrationResponse', to=sid, data=response)

    #if the radio does not get the assignment out of the meas config
    for radio in assignmentArr:
        sendAssignmentToRadio(radio)

# In[ --- TODO --- ]
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
    cbsd = None
    try:
        cbsd = getCBSDWithId(jsonData["spectrumData"]["cbsdId"])
    except KeyError:
        pass
    try:
        deviceInfo=jsonData["spectrumData"]
        cbsd.latitude = deviceInfo["latitude"]
        cbsd.longitude = deviceInfo["longitude"]
        # If simulating, dump previously logged data
        if(isSimulating):
            REM.objects = []
        if(deviceInfo["spectrumData"]):
            for rpmr in deviceInfo["spectrumData"]["rcvdPowerMeasReports"]:
                mr = measReportObjectFromJSON(rpmr)
                REM.measReportToSASREMObject(mr, cbsd)
    except KeyError as ke:
        print("rcvd power meas error: ")
        print(ke)

@socket.on("latencyTest")
def sendCurrentTime(sid):
    """Sends the simulation client the current server time. Used to calulcated latency."""
    responseDict = {"serverCurrentTime":time.time()}
    socket.emit('latencyTest', to=sid, data=json.dumps(responseDict))

@socket.on("simCheckPUAlert")
def simCheckPUAlert(sid, data):
    payload = json.loads(data)
    checkPUAlert(payload)

@socket.on("checkPUAlert")
def sendSimPuDetection(sid):
    checkPUAlert()

@socket.on("getPuDetections")
def printPuDetections(sid):
    global puDetections
    socket.emit("detections", json.dumps(puDetections))
    puDetections = {}

# IIC Functions ---------------------------------------
def getRandBool():
    """Randomly returns True or False"""
    return bool(random.getrandbits(1)) # Requires import random

def double_pad_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus):
    """Executes Double Pad Obfuscation Scheme"""

    pu_bw = puHighFreq - puLowFreq
    low_su_low_freq = puLowFreq - pu_bw
    low_su_high_freq = puLowFreq
    high_su_low_freq = puHighFreq
    high_su_high_freq = puHighFreq + pu_bw


    if(getRandBool()): # Randomly pick to pad top or bottom first
        if(low_su_low_freq >= SASAlgorithms.MINCBRSFREQ and est_num_of_available_sus):
            sendIICCommand(low_su_low_freq, low_su_high_freq)
            est_num_of_available_sus -= 1
        if(high_su_high_freq <= SASAlgorithms.MAXCBRSFREQ and est_num_of_available_sus):
            sendIICCommand(high_su_low_freq, high_su_high_freq)
            est_num_of_available_sus -= 1
    else:
        if(high_su_high_freq <= SASAlgorithms.MAXCBRSFREQ):
            sendIICCommand(high_su_low_freq, high_su_high_freq)
            est_num_of_available_sus -= 1
        if(low_su_low_freq >= SASAlgorithms.MINCBRSFREQ):
            sendIICCommand(low_su_low_freq, low_su_high_freq)
            est_num_of_available_sus -= 1

def fill_channel_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus):
    """Fills PU Occupied Channel(s)"""

    #Find the channel where the lowest PU frequency resides
    puLowChannel = getChannelFromFrequency(puLowFreq)
    channelFreqLow = getChannelFreqFromChannel(puLowChannel)
    lowCbsdBw = puLowFreq - channelFreqLow

    #Find the channel where the highest PU frequency resides
    puHighChannel = getChannelFromFrequency(puHighFreq)
    channelFreqHigh = getChannelFreqFromChannel(puHighChannel, getHighFreq=True)
    highCbsdBw = channelFreqHigh - puHighFreq
    
    # Only command radio if the obfuscating spectrum is at least 1 kHz
    if(highCbsdBw > 1000):
        sendIICCommand(puHighFreq, channelFreqHigh)   
    if(lowCbsdBw >= 1000):
        sendIICCommand(channelFreqLow, puLowFreq)


@socket.on('incumbentInformation')
def incumbentInformation(sid, data):
    """Function for PUs to send their operating data"""
    utilizeExtraChannel = True # TODO: Decide when to toggle this
    jsonData = json.loads(data)
    for data in jsonData["incumbentInformation"]:
        # Get time, location, and frequency range of PU
        desireObfuscation = None
        scheme = None
        startTime = None
        endTime = None
        puLat = None
        puLon = None
        puLowFreq = None
        puLighFreq = None
        power = None
        try:
            desireObfuscation = bool(data["desireObfuscation"])
            scheme = str(data["scheme"])
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
            endTime = data["endTime"]
        except:
            pass
        if(desireObfuscation):
            if(scheme):
                # global allRadios
                est_num_of_available_sus = 0
                for radio in allRadios:  
                    if not radio.justChangedParams:
                        est_num_of_available_sus += 1
                if(scheme == "double_pad"):
                    double_pad_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus)
                elif(scheme == "fill_channel"):
                    fill_channel_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus)
            else:
                print("No PU Obfuscation Scheme Detected...")     
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
    now = datetime.now(timezone.utc)
    if grant.heartbeatTime + timedelta(0, grant.heartbeatInterval) < now:
        removeGrant(grant.id, grant.cbsdId)
        print('grant ' + grant.id + ' canceled')

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
            # print("SENDING LOW: " +str(lowFreq)+" and HIGH: "+str(highFreq))
            sendObstructionToRadio(radio, lowFreq, highFreq)
            radiosToChangeBack.append(radio)
            threading.Timer(5.0, resetRadioStatuses, [radiosToChangeBack]).start()
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
    socket.emit("obstructChannelWithRadioParams", json.dumps(changeParams), room=cbsd.sid)


def checkPUAlert(data=None):
    report = []
    global puDetections
    freqRange = SASAlgorithms.MAXCBRSFREQ - SASAlgorithms.MINCBRSFREQ
    blocks = freqRange/SASAlgorithms.TENMHZ
    if(data):
        puDetections[str(data["reportId"])] = []
    for i in range(int(blocks)):
        low = (i * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        high = ((i + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        result = SASAlgorithms.isPUPresentREM(REM, low, high, None, None, None)
        if(result == 1):
            if(isSimulating):
                if(data):
                    puDetections[str(data["reportId"])].append({"reportId":data["reportId"],"timestamp":str(float("{:0.3f}".format(time.time()))),"lowFreq":low,"highFreq":high, "result":str(result)})
                report.append("PU FOUND")
            else:
                for grant in grants:
                    if SASAlgorithms.frequencyOverlap(low, high, SASAlgorithms.getLowFreqFromOP(grant.operationParam), SASAlgorithms.getHighFreqFromOP(grant.operationPARAM)):
                        cbsd = getCBSDWithId(grant.cbsdId)
                        cbsd.sid.emit('pauseGrant', { 'grantId' : grant.id })
        elif result == 0:
            if(isSimulating):
                report.append("PU NOT FOUND")
                # socket.emit("puStatus", data="PU NOT FOUND")
        elif(result == 2):
            if(isSimulating):
                report.append("NO SPECTRUM DATA")
                # socket.emit("puStatus", data="NO SPECTRUM DATA")

    if(isSimulating):
        # print(report)
        # for x in (puDetections[str(data["reportId"])]):
            #  print(x)
        # Write to a (CSV/JOSN) file
        pass
        # try:
        #     socket.emit("puStatus", to=allClients[0],  data="report")
        # except:
        #     pass
    else:
        threading.Timer(1, checkPUAlert).start()
   
# In[ --- main --- ]
if __name__ == '__main__':
    getSettings()
    if(not isSimulating):
        threading.Timer(3.0, checkPUAlert).start()
    # TODO: move to gunicorn
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
