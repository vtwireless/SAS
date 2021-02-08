import eventlet
import socketio
import requests
import json
import SASAlgorithms
import SASREM
import time
import WinnForum
import CBSD

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

def generateOperationParam(grantId):
    #move if needed
    operationParam = {}
    operationParam["operationFrequencyRange"]["highFrequency"] = 50000
    operationParam["operationFrequencyRange"]["lowFrequency"] = 49000
    return operationParam

def generateResponse(responseCode):
    response = {}
    response["responseCode"] = responseCode
    response["message"] = WinnForum.responseDecode(responseCode)
    return response

def sendPostRequest(parameters):
    parameters["SAS_KEY"] = SASKEY
    x = requests.post(POSTURL, parameters)
    print(x.text)
    return x.json()

def getSettings() :
    getAl = { "action": "getSettings"}
    SASAlgorithms.setGrantAlgorithm(sendGetRequest(getAl)["algorithm"])
    SASAlgorithms.setHeartbeatInterval = sendGetRequest(getAl)["heartbeatInterval"]
    print(SASAlgorithms.getGrantAlgorithm() + ' ' + str(SASAlgorithms.getHeartbeatInterval()))

def sendBroadcast(broadcastName, data):
    socket.broadcast.emit(broadcastName, data)

def addObjectToREM(spectrumData):
    obj = SASREM.SASREMObject(5, 50, "obj", 5, 3500000, 3550000, time.time() )
    REM.addREMObject(obj)

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
    return 50#time.time()#just generate using epoch time, not really that important, but is unique

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

def measReportFromJSON(json):
    measReport = WinnForum.RcvdPowerMeasReport(["measFrequency"], ["measBandwidth"], ["measRcvdPower"])
    mr = WinnForum.MeasReport([measReport])
    return mr

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
            

getSettings()

param = {
    "action": "getNodes"
    }
#y = sendGetRequest(param)
#print(y["nodes"])

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
    if sid in allRadios: allRadios.remove(sid)
    if sid in allSASs: allSASs.remove(sid)

@socket.on('registrationRequest')
def register(sid, data):
    jsonData = json.loads(data)
    print(jsonData)
    responseArr = []
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
        response = WinnForum.RegistrationResponse(id, None, SASAlgorithms.generateResponse(0))
        responseArr.append(response.asdict())
    socket.emit('registrationResponse', responseArr)

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
    socket.emit('deregistrationResponse', responseArr)   

@socket.on('grantRequest')
def grantRequest(sid, data):
    jsonData = json.loads(data)
    print(jsonData)
    responseArr = []
    for item in jsonData["grantRequest"]:
        item["secondaryUserID"] = item["cbsdId"]
        if "operationParam" in item:
            item["powerLevel"] = item["operationParam"]["maxEirp"]
            item["minFrequency"] = item["operationParam"]["operationFrequencyRange"]["lowFrequency"]
            item["maxFrequency"] = item["operationParam"]["operationFrequencyRange"]["highFrequency"]
        if "vtGrantParams" in item:
            item["approximateByteSize"] = item["vtGrantParams"]["approximateByteSize"]
            item["dataType"] = item["vtGrantParams"]["dataType"]
            item["mobility"] = item["vtGrantParams"]["mobility"]
            item["maxVelocity"] = item["vtGrantParams"]["maxVelocity"]
            item["preferredFrequency"] = item["vtGrantParams"]["preferredFrequency"]
            item["preferredBandwidth"] = item["vtGrantParams"]["preferredBandwidth"]
            item["minBandwidth"] = item["vtGrantParams"]["minBandwidth"]
            item["frequencyAbsolute"] = item["vtGrantParams"]["frequencyAbsolute"]
            item["dataType"] = item["vtGrantParams"]["dataType"]
            item["startTime"] = item["vtGrantParams"]["startTime"]
            item["endTime"] = item["vtGrantParams"]["endTime"]
            item["location"] = item["vtGrantParams"]["location"]
        item["action"] = "createGrantRequest"
        grantRequest = WinnForum.GrantRequest(item["cbsdId"], None)
        if "operationParam" in item:
            ofr = WinnForum.FrequencyRange(item["operationParam"]["operationFrequencyRange"]["lowFrequency"], item["operationParam"]["operationFrequencyRange"]["highFrequency"])
            op = WinnForum.OperationParam(item["operationParam"]["maxEirp"], ofr)
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
    socket.emit('grantResponse', responseArr)


@socket.on('heartbeatRequest')
def heartbeat(sid, data):
    jsonData = json.loads(data)
    hbrArray = []
    for hb in jsonData["heartbeatRequest"]:
        grant = getGrantWithID(hb["grantId"])
        try:
            if hb["measReport"]:
                mr = measReportFromJSON(hb["measReport"][0])#this should be an array
                REM.measReportToSASREMObject(mr, getCBSDWithId(hb["cbsdId"]))
        except KeyError:
            print("no measure report")
        response = SASAlgorithms.runHeartbeatAlgorithm(grants, REM, hb, grant)
        hbrArray.append(response.asdict())
    socket.emit('heartbeatResponse', hbrArray)

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
    socket.emit('relinquishmentResponse', relinquishArr)

@socket.on('changeSettings')
def changeAlgorithm(sid, data):
    getSettings()

@socket.on('spectrumData')
def spectrumData(sid, data):
    jsonData = json.loads(data)
    print(jsonData)
    REM.measReportToSASREMObject(jsonData["measReport"][0], jsonData["cbsdId"])



if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)