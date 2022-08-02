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
allRadios = []  # CBSDSocket
allWebApps = []
allSASs = []
grants = []
cbsds = []  # cbsd references

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


# In[ --- Helper Functions --- ]

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
        getAl = {"action": "getSettings"}
        result = sendGetRequest(getAl)
        SASAlgorithms.setGrantAlgorithm(result["algorithm"])
        SASAlgorithms.setHeartbeatInterval(result["heartbeatInterval"])
        SASAlgorithms.setREMAlgorithm(result["REMAlgorithm"])
    else:
        SASAlgorithms.setGrantAlgorithm('DEFAULT')
        SASAlgorithms.setHeartbeatInterval(5)
        SASAlgorithms.setREMAlgorithm('DEFAULT')
    print('GRANT: ' + SASAlgorithms.getGrantAlgorithm() + ' HB: ' + str(
        SASAlgorithms.getHeartbeatInterval()) + ' REM: ' + SASAlgorithms.getREMAlgorithm())


def sendBroadcast(broadcastName, data):
    socket.emit(broadcastName, data)


def getGrantWithID(grantId):
    for grant in grants:
        if str(grant.id) == str(grantId):
            return grant
    if databaseLogging:
        param = {"action": "getGrant", "grantId": grantId}
        res = sendGetRequest(param)
        if res["status"] == "1":
            return loadGrantFromJSON(res["grant"])
        else:
            print("false GrantId")
            return None
    else:
        return None


def loadGrantFromJSON(json):
    ofr = WinnForum.FrequencyRange(json["frequency"], json["frequency"] + json["bandwidth"])
    operationParam = WinnForum.OperationParam(json["requestPowerLevel"], ofr)
    vtgp = WinnForum.VTGrantParams(None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                                   None)
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
    return str(uuid.uuid4())  # time.time()#just generate using epoch time, not really that important, but is unique


def getCBSDWithId(cbsdId):
    for cbsd in cbsds:
        if str(cbsd.id) == str(cbsdId):
            return cbsd
    if databaseLogging:
        param = {"action": "getNode", "nodeId": cbsdId}
        res = sendGetRequest(param)
        if res["status"] == "1":
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
                     json["cbsdSerialNumber"], json["callSign"], json["cbsdCategory"], json["cbsdInfo"],
                     json["airInterface"], \
                     json["installationParam"], json["measCapability"], json["groupingParam"])
    allClients.append(cbsd)
    return cbsd


def measReportObjectFromJSON(json):
    return WinnForum.RcvdPowerMeasReport(float(json["measFrequency"]), json["measBandwidth"],
                                         json["measRcvdPower"] or 0)


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


@socket.on('getUsers')
def getSecondaryUsers(sid, data):
    response = db.get_secondary_users()
    socket.emit('getUsersResponse', to=sid, data=response)


@socket.on('getUser')
def getUser(sid, data):
    response = db.get_secondary_user(data)
    socket.emit('getUserResponse', to=sid, data=response)


# In[ --- Node Management ---]

@socket.on('getNodesRequest')
def getNodes(sid, payload):
    response = db.get_nodes()
    socket.emit('getNodesResponse', to=sid, data=response)


@socket.on('registrationRequest')
def register(sid, nodes):
    response, assignmentArr = db.register_nodes(sid, nodes)
    socket.emit('registrationResponse', to=sid, data=response)

    # if the radio does not get the assignment out of the meas config
    for radio in assignmentArr:
        sendAssignmentToRadio(radio)


@socket.on('deregistrationRequest')
def deregister(sid, data):
    response = db.deregister_nodes(data)
    socket.emit('deregistrationResponse', to=sid, data=response)


# In[ --- Grant Management --- ]

@socket.on('getGrantsRequest')
def getGrantRequests(sid, payload):
    response = db.get_grants()
    socket.emit('getGrantsResponse', to=sid, data=response)


@socket.on('grantRequest')
def grantRequest(sid, data):
    response = db.create_grant_request(data)
    socket.emit('grantResponse', to=sid, data=response)


@socket.on('heartbeatRequest')
def heartbeat(sid, data):
    response, grantArray = db.heartbeat_request(data)
    socket.emit('heartbeatResponse', to=sid, data=response)

    for grant in grantArray:
        threading.Timer(
            (grant.heartbeatInterval * 1.1) + 2, db.cancel_grant, [grant]
        ).start()


@socket.on('spectrumInquiryRequest')
def spectrumInquiryRequest(sid, data):
    response, radiosToCommunicate = db.spectrum_inquiry(data)
    socket.emit('spectrumInquiryResponse', to=sid, data=response)

    for radio in radiosToCommunicate:
        socket.emit(
            "changeRadioParams", data=radio['data'], room=radio['room']
        )


@socket.on('relinquishmentRequest')
def relinquishment(sid, data):
    response, radiosToCommunicate = db.relinquishment_request(data)
    socket.emit('relinquishmentResponse', to=sid, data=response)


# In[ --- PU Detections Management --- ]

@socket.on("simCheckPUAlert")
def simCheckPUAlert(sid, data):
    checkPUAlert(data)


@socket.on("checkPUAlert")
def sendSimPuDetection(sid):
    checkPUAlert()


@socket.on("getPuDetections")
def printPuDetections(sid):
    response = db.get_pudetections()
    socket.emit('detections', to=sid, data=response)


# In[ --- Others --- ]

@socket.on("latencyTest")
def sendCurrentTime(sid):
    """Sends the simulation client the current server time. Used to calulcated latency."""
    response = {
        "serverCurrentTime": time.time()
    }
    socket.emit('latencyTest', to=sid, data=response)


@socket.on('changeSettings')
def changeAlgorithm(sid, data):
    getSettings()


@socket.on('spectrumData')
def spectrumData(sid, data):
    db.spectrumData(data)


# In[ --- TODO --- ]
# In[ --- IIC Functions --- ]
def getRandBool():
    """Randomly returns True or False"""
    return bool(random.getrandbits(1))  # Requires import random


def double_pad_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus):
    """Executes Double Pad Obfuscation Scheme"""

    pu_bw = puHighFreq - puLowFreq
    low_su_low_freq = puLowFreq - pu_bw
    low_su_high_freq = puLowFreq
    high_su_low_freq = puHighFreq
    high_su_high_freq = puHighFreq + pu_bw

    if (getRandBool()):  # Randomly pick to pad top or bottom first
        if (low_su_low_freq >= SASAlgorithms.MINCBRSFREQ and est_num_of_available_sus):
            sendIICCommand(low_su_low_freq, low_su_high_freq)
            est_num_of_available_sus -= 1
        if (high_su_high_freq <= SASAlgorithms.MAXCBRSFREQ and est_num_of_available_sus):
            sendIICCommand(high_su_low_freq, high_su_high_freq)
            est_num_of_available_sus -= 1
    else:
        if (high_su_high_freq <= SASAlgorithms.MAXCBRSFREQ):
            sendIICCommand(high_su_low_freq, high_su_high_freq)
            est_num_of_available_sus -= 1
        if (low_su_low_freq >= SASAlgorithms.MINCBRSFREQ):
            sendIICCommand(low_su_low_freq, low_su_high_freq)
            est_num_of_available_sus -= 1


def fill_channel_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus):
    """Fills PU Occupied Channel(s)"""

    # Find the channel where the lowest PU frequency resides
    puLowChannel = getChannelFromFrequency(puLowFreq)
    channelFreqLow = getChannelFreqFromChannel(puLowChannel)
    lowCbsdBw = puLowFreq - channelFreqLow

    # Find the channel where the highest PU frequency resides
    puHighChannel = getChannelFromFrequency(puHighFreq)
    channelFreqHigh = getChannelFreqFromChannel(puHighChannel, getHighFreq=True)
    highCbsdBw = channelFreqHigh - puHighFreq

    # Only command radio if the obfuscating spectrum is at least 1 kHz
    if (highCbsdBw > 1000):
        sendIICCommand(puHighFreq, channelFreqHigh)
    if (lowCbsdBw >= 1000):
        sendIICCommand(channelFreqLow, puLowFreq)


@socket.on('incumbentInformation')
def incumbentInformation(sid, data):
    """Function for PUs to send their operating data"""
    utilizeExtraChannel = True  # TODO: Decide when to toggle this
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
        if (desireObfuscation):
            if (scheme):
                # global allRadios
                est_num_of_available_sus = 0
                for radio in allRadios:
                    if not radio.justChangedParams:
                        est_num_of_available_sus += 1
                if (scheme == "double_pad"):
                    double_pad_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus)
                elif (scheme == "fill_channel"):
                    fill_channel_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus)
            else:
                print("No PU Obfuscation Scheme Detected...")
        else:
            pass  # PU does not want special treatment


def getChannelFreqFromChannel(channel, getHighFreq=False):
    """Convert a channel integer to a freq for the channel"""
    if (getHighFreq):
        channel = channel + 1
    return (channel * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ


def getChannelFromFrequency(freq):
    """Returns the lowFreq for the channel 'freq' can be found"""
    for channel in range(NUM_OF_CHANNELS):
        if (freq < ((channel + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ):
            return channel
    return None


def initiateSensing(lowFreq, highFreq):
    count = 0
    radioCountLimit = 3
    radiosToChangeBack = []
    # loop through radios, set 3 as the limit
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
        if count >= radioCountLimit or count > len(allRadios) / 3:
            # don't use more than 1/3 of the radios to check band
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
    freqRange = SASAlgorithms.MAXCBRSFREQ - SASAlgorithms.MINCBRSFREQ  # 3.5 GHz CBRS Band is 150 MHz wide
    blocks = freqRange / SASAlgorithms.TENMHZ
    for i in range(int(blocks)):
        low = (i * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        high = ((i + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        result = SASAlgorithms.isPUPresentREM(REM, low, high, None, None, None)
        if result == 2:
            # if there is no spectrum data available for that frequency range assign radio to it
            changeParams = dict()
            changeParams["lowFrequency"] = str((SASAlgorithms.TENMHZ * i) + SASAlgorithms.MINCBRSFREQ)
            changeParams["highFrequency"] = str((SASAlgorithms.TENMHZ * (i + 1)) + SASAlgorithms.MINCBRSFREQ)
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
            # loop through radios, set 3 as the limit
            for radio in allRadios:
                if not radio.justChangedParams:
                    sendObstructionToRadio(radio, lowFreq, highFreq)
                    radiosToChangeBack.append(radio)
                    count = count + 1
                if count >= radioCountLimit or count > len(allRadios) / 3:
                    # don't use more than 1/3 of the radios to check band
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
                            if count >= radioCountLimit or count > len(allRadios) / 3:
                                # don't use more than 1/3 of the radios to check band
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
    report, pauseArr = db.check_pudetections(data)
    for item in pauseArr:
        socket.emit('pauseGrant', to=item['sid'], data={'grantId': item['grantId']})

    # TODO: Check if we need to return anything
    # return report

    threading.Timer(1, checkPUAlert).start()


# In[ --- main --- ]
if __name__ == '__main__':
    getSettings()
    if not isSimulating:
        threading.Timer(3.0, checkPUAlert).start()
    # TODO: move to gunicorn
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
