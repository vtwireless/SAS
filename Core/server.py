import eventlet
import socketio
import requests
import json
import SASAlgorithms
import SASREM
import time
from datetime import datetime, timedelta
import WinnForum
import CBSD
import threading
import uuid

GETURL = "http://localhost/SASAPI/SAS_API_GET.php"
POSTURL = "http://localhost/SASAPI/SAS_API.php"
SASKEY = "qowpe029348fuqw9eufhalksdjfpq3948fy0q98ghefqi"

allClients = []
allRadios = []
allWebApps = []
allSASs = []
grants = []
cbsds = []

databaseLogging = False

socket = socketio.Server()
app = socketio.WSGIApp(socket, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()

def sendGetRequest(parameters):
    parameters["SAS_KEY"] = SASKEY
    x = requests.post(GETURL, parameters)
    return x.json()


def generateResponse(responseCode):
    response = {}
    response["responseCode"] = str(esponseCode)
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
    socket.broadcast.emit(broadcastName, data)

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
    return WinnForum.RcvdPowerMeasReport(json["measFrequency"], json["measBandwidth"], json["measRcvdPower"] or 0)

def removeGrant(grant, cbsdId):
    for g in grants:
        if str(g.id) == str(grant.id) and str(g.cbsdId) == str(cbsdId):
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

@socket.event
def my_message(sid, data):
    print('message ', data)

@socket.event
def disconnect(sid):
    print('disconnect ', sid)
    allClients.remove(sid)
    if sid in allWebApps: allWebApps.remove(sid)
    if sid in allSASs: allSASs.remove(sid)
    for radio in allRadios:
        if radio.sid == sid:
            allRadios.remove(radio)


#@socket.on('isSensingRadio')
#def isSensingRadio(sid, data):
#    sendAssignmentToRadio(sid)



@socket.on('registrationRequest')
def register(sid, data):
    jsonData = json.loads(data)
    responseArr = []
    assignmentArr = []
    for item in jsonData["registrationRequest"]:
        if "vtParams" in item:
            item["nodeType"] = item["vtParams"]["nodeType"]
            item["minFrequency"] = item["vtParams"]["minFrequency"]
            item["maxFrequency"] = item["vtParams"]["maxFrequency"]
            item["minSampleRate"] = item["vtParams"]["minSampleRate"]
            item["maxSampleRate"] = item["vtParams"]["maxSampleRate"]
            item["mobility"] = item["vtParams"]["isMobile"]
        if "installationParam" in item:
            if "latitude" in item["installationParam"] and "longitude" in item["installationParam"]:
                item["location"] = str(item["installationParam"]["latitude"]) + ',' + str(item["installationParam"]["longitude"])
        item["IPAddress"] = 'TODO IP'
        item["action"] = "createNode"
        id = ''
        if databaseLogging:
            print(sendPostRequest(item))
            id = 'TODO'
        else:
            radio = CBSD.CBSD(generateId(), 5, item["fccId"])
            id = radio.id
            allClients.append(radio)
            cbsds.append(radio)
        if "measReportCapability" in item:#if the registering entity is a radio add it to the array and give it an assignment
            cbsd = SASREM.CBSDSocket(id, sid, False)
            assignmentArr.append(cbsd)
            response.measReportConfig = item["measReportCapability"]
        response = WinnForum.RegistrationResponse(id, None, SASAlgorithms.generateResponse(0))
        responseArr.append(response.asdict())
    responseDict = {"registrationResponse":responseArr}
    print(responseDict)
    socket.emit('registrationResponse', json.dumps(responseDict))
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
            responseArr.append(response)
        success = removeCBSD(item["cbsdId"])
        response = WinnForum.DeregistrationResponse()
        if success:
            response.cbsdId = item["cbsdId"]
            response.response = generateResponse(0)
        else:
            response.cbsdId = item["cbsdId"]
            response.response = generateResponse(103)
        responseArr.append(response.asdict())
    responseDict = {"deregistrationResponse":responseArr}
    socket.emit('deregistrationResponse', json.dumps(responseDict))   

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
        if grantResponse.response.responseCode == 0:
            g = WinnForum.Grant(grantResponse.grantId, item["cbsdId"], grantResponse.operationParam, vtgp, grantResponse.grantExpireTime)
            grants.append(g)
        responseArr.append(grantResponse.asdict())
    responseDict = {"grantResponse":responseArr}
    socket.emit('grantResponse', json.dumps(responseDict))

@socket.on('heartbeatRequest')
def heartbeat(sid, data):
    jsonData = json.loads(data)
    hbrArray = []
    for hb in jsonData["heartbeatRequest"]:
        cbsd = getCBSDWithId(hb["cbsdId"])
        grant = getGrantWithID(hb["grantId"])
        try:
            if hb["measReport"]:
                for rpmr in hb["measReport"]["rcvdPowerMeasReports"]:
                    mr = measReportObjectFromJSON(rpmr)#this should be an array
                    REM.measReportToSASREMObject(mr, cbsd)
        except KeyError:
            print("no measure report")
        response = SASAlgorithms.runHeartbeatAlgorithm(grants, REM, hb, grant)
        grant.heartbeatTime = datetime.now()
        grant.heartbeatInterval = response.heartbeatInterval
        threading.Timer(response.heartbeatInterval*1.1, cancelGrant, grant).start()

        hbrArray.append(response.asdict())
    responseDict = {"heartbeatResponse":hbrArray}
    socket.emit('heartbeatResponse', json.dumps(responseDict))

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
        success = removeGrant(getGrantWithID(relinquishmentRequest["grantId"]), relinquishmentRequest["cbsdId"])
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
    socket.emit('relinquishmentResponse', json.dumps(responseDict))

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
    socket.emit('spectrumInquiryResponse', json.dumps(responseDict))

@socket.on('changeSettings')
def changeAlgorithm(sid, data):
    getSettings()

@socket.on('spectrumData')
def spectrumData(sid, data):
    jsonData = json.loads(data)
    cbsd = None
    try:
        cbsd = getCBSDWithId(jsonData["cbsdId"])
    except KeyError:
        pass
    try:
        if jsonData["spectrumData"]:
            for rpmr in jsonData["spectrumData"]["rcvdPowerMeasReports"]:
                mr = measReportObjectFromJSON(rpmr)
                REM.measReportToSASREMObject(mr, cbsd)
    except KeyError:
        print("rcvd power meas error")


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
            radio.emit("changeRadioParams", changeParams)
            radiosToChangeBack.append(radio)
        if count >= radioCountLimit or count > radio.length/3:
        #don't use more than 1/3 of the radios to check band
            break
    
    threading.Timer(3.0, resetRadioStatuses, radiosToChangeBack).start()

def resetRadioStatuses(radios):
    for radio in radios:
        radio.justChangedParams = False

def cancelGrant(grant):
    now = datetime.now()
    if grant.heartbeatTime + datetime.timedelta(0, grant.heartbeatInterval) < now:
        removeGrant(grant.id, grant.cbsdId)
        print('grant ' + grant.id + ' canceled')


def sendAssignmentToRadio(cbsd):
    print("a sensing radio has joined")
    if cbsd in allRadios:
        allRadios.remove(cbsd)
    allRadios.append(cbsd)
    freqRange = 3700000000 - 3550000000
    tenMHz = 10000000
    blocks = freqRange/10000000
    for i in range(blocks):
        low = i * tenMHz
        high = (i + 1) * tenMHz
        result = SASAlgorithms.isPUPresentREM(REM, low, high, None, None, None)
        if result == 2:
            #if there is no spectrum data available for that frequency range assign radio to it
            changeParams = dict()
            changeParams["lowFrequency"] = tenMHz * i
            changeParams["highFrequency"] = tenMHz * (i+ 1)
            changeParams["cbsd"] = cbsd.id
            cbsd.justChangedParams = True
            socket.emit("changeRadioParams", changeParams)
            break
    
    threading.Timer(3.0, resetRadioStatuses, [cbsd]).start()

def checkPUAlert():
    freqRange = 3700000000 - 3550000000
    tenMHz = 10000000
    blocks = freqRange/10000000
    for i in range(int(blocks)):
        low = i * tenMHz
        high = (i + 1) * tenMHz
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