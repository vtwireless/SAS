"""
Very similar to server.py

Revised: March 20, 2021
Authored by: Cameron Makin (cammakin8@vt.edu), Joseph Tolley (jtolley@vt.edu)
Advised by Dr. Carl Dietrich (cdietric@vt.edu)
For Wireless@VT

Revised March 27, 2023
Modified by: Oren Rodney Collaco (orenrc@vt.edu)
Advised by Aloizio Pereira da Silva (aloiziops@vt.edu)
For Commonwealth Cyber Initiavtive (CCI)
"""

from ast import Global

import eventlet #pip install eventlet
eventlet.monkey_patch()
import socketio #pip install socketio
import requests
import json
from algorithms import SASAlgorithms
from algorithms import SASREM
import time
from datetime import datetime, timedelta, timezone
from algorithms import Server_WinnForum as WinnForum
from algorithms import CBSD
import threading
import uuid
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

from threading import Thread
from time import sleep
import ssl
from io import BytesIO
import os
from SensorProcessing import SensorProcessor


GETURL = "http://localhost/SASAPI/SAS_API_GET.php"
POSTURL = "http://localhost/SASAPI/SAS_API.php"
SASKEY = "qowpe029348fuqw9eufhalksdjfpq3948fy0q98ghefqi"
RESERVATION_URL = "http://localhost:9258/"

############################### Global variables start ###################################################

allClients = []
allRadios = [] #CBSDSocket
allWebApps = []
allSASs = []
grants = []
cbsds = [] #cbsd references
CbsdList = []
SpectrumList = []

databaseLogging = False
isSimulating = True
NUM_OF_CHANNELS = 15
puDetections = {}


DyanmicProtectionAreas = [
     {
         "id": "DPA-HCRO",
         "name":"HCRO",
         "latitude": 40.817132,
         "longitude": -121.470741,
         "radius": 200000,  # in metres
         "activationTime": "2023-03-25T05:55:00Z",
         "deactivationTime": "2023-03-25T08:10:00Z",
         "active": False,
         "spectrum": [ [3550000000, 3590000000] ]
     }
 ]

############################### Global variables end ###################################################


socket = socketio.Server(async_mode='eventlet', cors_allowed_origins='*')
app = socketio.WSGIApp(socket, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})
# eventlet.monkey_patch()

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()


@socket.on('test')
def test(id, data):
    print("Received event:" + data)
    socket.emit("test", "hi")

def sendGetRequest(parameters):
    parameters["SAS_KEY"] = SASKEY
    x = requests.post(GETURL, parameters)
    return x.json()

def generateResponse(responseCode):
    response = {}
    response["responseCode"] = int(str(responseCode))
    response["responseMessage"] = WinnForum.responseDecode(responseCode)
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
        SASAlgorithms.setHeartbeatInterval(8)
        SASAlgorithms.setREMAlgorithm('DEFAULT')
    print('GRANT: ' + SASAlgorithms.getGrantAlgorithm() + ' HB: ' + str(SASAlgorithms.getHeartbeatInterval()) + ' REM: ' + SASAlgorithms.getREMAlgorithm())

def sendBroadcast(broadcastName, data):
    socket.emit(broadcastName, data)

#def addObjectToREM(spectrumData):
#     obj = SASREM.SASREMObject(5, 50, "obj", 5, 3500000, 3550000, time.time() )
#    REM.addREMObject(obj)

def getGrantWithID(grantId):
    print("Total grants: " + str(len(grants)))
    print("Requesting grant: " + str(grantId))
    for grant in grants:
        print("Grant: " + str(grant.id))
        if str(grant.id) == str(grantId):
            print("Grant found")
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
        print("Grant not found")
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
            print(g)
            print("Deleting grant: " + str(grantId) + " from CBSD: " + str(cbsdId) + " from list")
            grants.remove(g)
            return True
    return False

def terminateGrant(grantId, cbsdId):
    for g in grants:
        if str(g.id) == str(grantId) and str(g.cbsdId) == str(cbsdId):
            print("Terminating grant: " + str(grantId) + " from CBSD: " + str(cbsdId) + " from list")
            g.status = "TERMINATED"
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
    #allClients.append(sid)

@socket.event
def disconnect(sid):
    print('disconnect ', sid)
    #allClients.remove(sid)
    if sid in allWebApps: allWebApps.remove(sid)
    if sid in allSASs: allSASs.remove(sid)
    for radio in allRadios:
        if radio.sid == sid:
            allRadios.remove(radio)

@socket.on('getCbsdList')
def sendCbsdList(id, data):
    global CbsdList
    socket.emit('cbsdUpdate', CbsdList)

@socket.on('getDpaList')
def sendDpaList(id, data):
    global DyanmicProtectionAreas
    socket.emit('dpaUpdate', DyanmicProtectionAreas)

############################################### Incumbent Detection #########################################################

# Global dictionary to keep track of the count of consecutive IncumbentDetected values for each channel
consecutive_counts = {}

def signalDetected(channel, incumbent_detected, sensorInfo, x=3, allowed_misses=2):
    global consecutive_counts

    # Get sensorId from sensorInfo
    sensorId = sensorInfo["sensor_id"]

    print("Signal detected on channel " + str(channel) + " by sensor " + str(sensorId) + " with incumbent_detected = " + str(incumbent_detected))

    # Initialize channel count if not already present in consecutive_counts
    if channel not in consecutive_counts:
        consecutive_counts[channel] = 0

    # Check if incumbent_detected is true or false and update consecutive_counts accordingly
    if incumbent_detected:
        consecutive_counts[channel] = min(consecutive_counts[channel] + 1, x + allowed_misses)
    else:
        consecutive_counts[channel] = max(consecutive_counts[channel] - 1, -(x + allowed_misses))

    # Call activateIncumbentProtection or deactivateIncumbentProtection based on consecutive_counts
    if consecutive_counts[channel] >= x:
        activateIncumbentProtection(channel, sensorInfo)
        print(f"Activated incumbent protection for Channel {channel} by Sensor {sensorId}")
    elif consecutive_counts[channel] <= -x:
        # deactivateIncumbentProtection(channel, sensorInfo)
        print(f"Deactivated incumbent protection for Channel {channel} by Sensor {sensorId}")

def activateIncumbentProtection(channel, sensorInfo):

    # Get sensorId from sensorInfo
    sensorId = sensorInfo["sensor_id"]
    sensorLat = sensorInfo["lat"]
    sensorLon = sensorInfo["lon"]

    # Check if grant already exists for the channel and sensorId
    for grant in grants:
        # check if sensorId exists in grant id string
        print(grant)
        if sensorId in grant.id:
            # check if channel exists in grant id string (like "channel1")
            if "channel" + str(channel) in grant.id:
                # check if grant is already active
                if hasattr(grant, "status"):
                    if(grant.status != "TERMINATED"):
                        print(f"Grant already exists for Channel {channel} by Sensor {sensorId}")
                        return
                else:
                    print(f"Grant already exists for Channel {channel} by Sensor {sensorId}")
                    grant.endTime = datetime.now(timezone.utc) + timedelta(seconds=5)
                    return
    # Create a new incumbent protection grant
    print(f"Creating new incumbent protection grant for Channel {channel} by Sensor {sensorId}")
    IncumbentGrant = SASAlgorithms.createIncumbentGrant(sensorInfo, channel, grants, CbsdList, SpectrumList, socket)
    IncumbentGrant.isIncumbentProtection = True
    IncumbentGrant.endTime = datetime.now(timezone.utc) + timedelta(seconds=5)
    grants.append(IncumbentGrant)

def checkIncumbentProtectionGrants():
    while True:
        # print("Checking incumbent protection grants")
        for grant in grants:
            if hasattr(grant, "isIncumbentProtection"):
                if grant.isIncumbentProtection:
                    if datetime.now(timezone.utc) > grant.endTime:
                        print("Deleting incumbent protection grant " + str(grant.id) + " from list")
                        grants.remove(grant)
        time.sleep(1)


# Thread to check for expired incumbent protection grants and remove them
thread = threading.Thread(target=checkIncumbentProtectionGrants)
thread.start()


###############################################################################################################################


################################################# Dynamic Protected Areas #####################################################

# Function that checks if dynamic protection areas startTime are approaching and if so, activate them
def checkDynamicProtectionAreas():
    while True:
        print("Checking dynamic protection areas")
        for area in DyanmicProtectionAreas:
            if area["active"] == False:
                if datetime.now(timezone.utc) > datetime.fromisoformat(area["activationTime"].replace('Z', '+00:00')):
                    # Check if the deactivation time is in the past
                    if datetime.now(timezone.utc) > datetime.fromisoformat(area["deactivationTime"].replace('Z', '+00:00')):
                        continue
                    area["active"] = True
                    print("Activating dynamic protection area " + area["id"] + "...")
                    DpaGrant = SASAlgorithms.createDPAGrant(area, grants, CbsdList, SpectrumList, socket)
                    grants.append(DpaGrant)
                    socket.emit('dpaUpdate', DyanmicProtectionAreas)
                    print("Dynamic protection area " + area["id"] + " activated")
            # If the area is active, check if it should be deactivated
            else:
                if datetime.now(timezone.utc) > datetime.fromisoformat(area["deactivationTime"].replace('Z', '+00:00')):
                # Check if active
                    if area["active"] == True:
                        area["active"] = False
                        print("Dynamic protection area " + area["id"] + " deactivated")
                        # Remove the DPA grant
                        for grant in grants:
                            if grant.id == area["id"]:
                                terminateGrant(grant.id, area["id"])
                                socket.emit('dpaUpdate', DyanmicProtectionAreas)
        time.sleep(1)


def is_reservation_json(json_data):
    if "transactionId" in json_data and "dateTimePublished" in json_data and "scheduledEvents" in json_data:
        if json_data["scheduledEvents"]:
            return True
    return False

def reservation_json_to_dpa_json(json_data):
    if not json_data["scheduledEvents"]:
        return None

    activation_time = datetime.fromisoformat(json_data['scheduledEvents'][0]['dateTimeStart'].replace("Z", "+00:00"))
    deactivation_time = datetime.fromisoformat(json_data['scheduledEvents'][0]['dateTimeEnd'].replace("Z", "+00:00"))

    dpa_json = {
        "id": json_data['scheduledEvents'][0]['dpaId'],
        "name": json_data['scheduledEvents'][0]['dpaName'],
        "latitude": json_data['scheduledEvents'][0]['latitude'],
        "longitude": json_data['scheduledEvents'][0]['longitude'],
        "radius": json_data['scheduledEvents'][0]['dpaRadius'],
        "activationTime": activation_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "deactivationTime": deactivation_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active": False,
        "spectrum": json_data['scheduledEvents'][0]['channels']
    }
    return dpa_json

def convert_json_files_to_dpa_objects(relative_path):
    dpa_objects = []
    path = os.path.join(os.getcwd(), relative_path)

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    try:
                        json_data = json.load(f)
                        if is_reservation_json(json_data):
                            dpa_object = reservation_json_to_dpa_json(json_data)
                            if dpa_object:
                                deactivation_time = datetime.fromisoformat(dpa_object["deactivationTime"].replace("Z", "+00:00"))
                                current_time = datetime.now(timezone.utc)
                                if current_time < deactivation_time:
                                    dpa_objects.append(dpa_object)
                                else:
                                    print("Reservation is in the past. Ignored.")
                    except json.JSONDecodeError:
                        pass

    return dpa_objects



def checkReservationRequests():
    while True:
        print("Checking reservation requests")
        try:
            DPAs = convert_json_files_to_dpa_objects("../")
            for DPA in DPAs:
                conflict_found = False
                same_reservation = False

                for area in DyanmicProtectionAreas:
                    if area["id"] == DPA["id"]:
                        same_reservation = True
                        break

                    area_activation = datetime.fromisoformat(area["activationTime"].replace("Z", "+00:00"))
                    area_deactivation = datetime.fromisoformat(area["deactivationTime"].replace("Z", "+00:00"))
                    DPA_activation = datetime.fromisoformat(DPA["activationTime"].replace("Z", "+00:00"))
                    DPA_deactivation = datetime.fromisoformat(DPA["deactivationTime"].replace("Z", "+00:00"))

                    if (area_activation <= DPA_activation < area_deactivation) or (
                        area_activation < DPA_deactivation <= area_deactivation
                    ):
                        distance = SASAlgorithms.calculateDistance((area["latitude"], area["longitude"]), (DPA["latitude"], DPA["longitude"]))
                        if distance < (area["radius"] + DPA["radius"]):
                            for area_spectrum in area["spectrum"]:
                                for DPA_spectrum in DPA["spectrum"]:
                                    if (
                                        (area_spectrum[0] <= DPA_spectrum[0] < area_spectrum[1])
                                        or (area_spectrum[0] < DPA_spectrum[1] <= area_spectrum[1])
                                    ):
                                        conflict_found = True
                                        break
                                if conflict_found:
                                    break
                    if conflict_found:
                        break

                if same_reservation:
                    print(f"Exact same reservation already exists.")
                elif conflict_found:
                    print(f"Conflict found between {area['id']} and new DPA reservation request.")
                    # uploadStatus(DPA['id'], 'denied')
                else:
                    print(f"No conflict found for new DPA reservation request.")
                    # uploadStatus(DPA['id'], 'confirmed')
                    DyanmicProtectionAreas.append(DPA)
                    print("Updated DPA list:")
                    print(DyanmicProtectionAreas)

        except Exception as e:
            print(f"Error while processing reservation requests: {str(e)}")
        # Add sleep or wait time if necessary, for example, checking every 5 minutes
        # import time
        time.sleep(5)

# Thread to check if new DPA reservation requests are available
thread = threading.Thread(target=checkReservationRequests)
thread.start()

# Thread to check if dynamic protection areas are approaching
thread = threading.Thread(target=checkDynamicProtectionAreas)
sleep(5)
thread.start()

################################################################################################################################################

@socket.on('registrationRequest')
def register(sid, data):
    global CbsdList
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
        """ Create a JSON with all the details of the CBSD and append to the list """
        item["position"]={}
        item["spectrum"]={
            'subband': 0,
            'low': 0,
            'high': 0,
        }
        item["cbsdId"] = radio.id
        item["position"]["lat"] = item["installationParam"]["latitude"]
        item["position"]["lng"] = item["installationParam"]["longitude"]
        item["state"] = 1
        item["stateText"] = "Registered"
        if(item['fccId'] == "CCI-CBRS-PAL"):
            item["accessPriority"] = "PAL"
        else:
            item["accessPriority"] = "GAA"
        CbsdList.append(item)

    responseDict = {"registrationResponse":responseArr}
    #print(responseDict)
    print("Pinging webserver about the successfully registration")
    #socket.emit('registrationResponse', json.dumps(responseDict))
    # global socket
    socket.emit('cbsdUpdate', CbsdList)

    #if the radio does not get the assignment out of the meas config
    for radio in assignmentArr:
        sendAssignmentToRadio(radio)
    return json.dumps(responseDict)

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
        for cbsd in list(CbsdList):
            if (cbsd['cbsdId'] == item['cbsdId']):
                CbsdList.remove(cbsd)
    responseDict = {"deregistrationResponse":responseArr}
    socket.emit('cbsdUpdate', CbsdList)

    socket.emit('deregistrationResponse', to=sid, data=json.dumps(responseDict))
    return json.dumps(responseDict)

def computeSubband(low, high):
    if low == 3550000000 and high == 3560000000:
        return 1
    if low == 3560000000 and high == 3570000000:
        return 2
    if low == 3570000000 and high == 3580000000:
        return 3
    if low == 3580000000 and high == 3590000000:
        return 4
    if low == 3590000000 and high == 3600000000:
        return 5
    if low == 3600000000 and high == 3610000000:
        return 6
    if low == 3610000000 and high == 3620000000:
        return 7
    if low == 3620000000 and high == 3630000000:
        return 8
    if low == 3630000000 and high == 3640000000:
        return 9
    if low == 3640000000 and high == 3650000000:
        return 10
    if low == 3650000000 and high == 3660000000:
        return 11
    if low == 3660000000 and high == 3670000000:
        return 12
    if low == 3670000000 and high == 3680000000:
        return 13
    if low == 3680000000 and high == 3690000000:
        return 14
    if low == 3690000000 and high == 3700000000:
        return 15

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
            for radio in allClients:
                if(radio.id == item["cbsdId"]):
                    print(radio.id)
                    print(radio.latitude)
                    print(radio.longitude)
                    grantRequest.lat = radio.latitude
                    grantRequest.long = radio.longitude
            grantRequest.operationParam = op
        vtgp = None
        if "vtGrantParams" in item:
            vt = item["vtGrantParams"]
            vtgp = WinnForum.VTGrantParams(None, None, vt["preferredFrequency"], vt["frequencyAbsolute"], vt["minBandwidth"], vt["preferredBandwidth"], vt["preferredBandwidth"], vt["startTime"], vt["endTime"], vt["approximateByteSize"], vt["dataType"], vt["powerLevel"], vt["location"], vt["mobility"], vt["maxVelocity"])
            grantRequest.vtGrantParams = vtgp
        grantRequest.dist = SASAlgorithms.calculateInterferenceRadius(grantRequest)
        grantResponse = SASAlgorithms.runGrantAlgorithm(grants, REM, grantRequest, CbsdList, SpectrumList, socket)#algorithm
        if databaseLogging:
            sendPostRequest(item)#Database log
        else:
            grantResponse.grantId = generateId()
        if grantResponse.response.responseCode == "0":
            g = WinnForum.Grant(grantResponse.grantId, item["cbsdId"], grantResponse.operationParam, vtgp, grantResponse.grantExpireTime)
            g.lat = grantRequest.lat
            g.long = grantRequest.long
            g.dist = SASAlgorithms.calculateInterferenceRadius(grantRequest)
            g.IsDPA = False
            grants.append(g)
            subband = computeSubband(item["minFrequency"], item["maxFrequency"])
            SpectrumInfo = {
                'subband': subband,
                'low': item["minFrequency"],
                'high': item["maxFrequency"],
                'cbsdId': item["cbsdId"],
                'state': 2,
                'stateText': "Granted",
                'power': item["powerLevel"],
            }
            for i, cbsd in enumerate(CbsdList):
                if(cbsd['cbsdId'] == item['cbsdId']):
                    cbsd['state'] = 2
                    cbsd['stateText'] = "Granted"
                    cbsd["spectrum"]={
                        'subband': subband,
                        'low': str(round(int(item["minFrequency"])/1000000000, 3)),
                        'high': str(round(int(item["maxFrequency"])/1000000000, 3)),
                        'power': item["powerLevel"],

                    }
                    cbsd['distance'] = grantRequest.dist
                    CbsdList[i] = cbsd
                    SpectrumInfo['accessPriority'] = cbsd['accessPriority']
                    SpectrumInfo['fccId'] = cbsd['fccId']
            InsertCbsdInSpectrumList = True
            # Check if the cbsd is already in the spectrum list
            for i, spectrum in enumerate(SpectrumList):
                if SpectrumInfo["cbsdId"] == spectrum["cbsdId"]:
                    SpectrumList[i] = SpectrumInfo
                    InsertCbsdInSpectrumList = False
            if(InsertCbsdInSpectrumList):
                SpectrumList.append(SpectrumInfo)
            socket.emit('spectrumUpdate', SpectrumList)
            socket.emit('cbsdUpdate', CbsdList)

            print(SpectrumList)
            responseArr.append(grantResponse.asdict())
        else:
            responseArr.append(grantResponse.asdict())
    responseDict = {"grantResponse":responseArr}
    socket.emit('grantResponse', to=sid, data=json.dumps(responseDict))
    return json.dumps(responseDict)

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
        IsTerminated = False
        if(hasattr(grant, 'status')):
            if(grant.status == "TERMINATED"):
                IsTerminated = True
        if grant != None and not IsTerminated:
            grant.heartbeatTime = datetime.now(timezone.utc)
            grant.heartbeatInterval = response.heartbeatInterval
            hbrArray.append(response.asdict())
            for i, item in enumerate(SpectrumList):
                if(item['cbsdId'] == hb['cbsdId']):
                    item['state'] = 3
                    item['stateText'] = "Authorized"
                    SpectrumList[i] = item
            for i, cbsd in enumerate(CbsdList):
                if(cbsd['cbsdId'] == hb['cbsdId']):
                    cbsd['state'] = 3
                    cbsd['stateText'] = "Authorized"
                    CbsdList[i] = cbsd
        else:
            hbrArray.append(response.asdict())
    socket.emit('spectrumUpdate', SpectrumList)
    socket.emit('cbsdUpdate', CbsdList)
    responseDict = {"heartbeatResponse":hbrArray}
    socket.emit('heartbeatResponse', to=sid, data=json.dumps(responseDict))

    for g in grantArray:
        if response.heartbeatInterval != None:
            threading.Timer((response.heartbeatInterval*1.2)+2, cancelGrant, [g]).start()
            print("Terminating grant in " + str((response.heartbeatInterval*1.5)+2) + " seconds")
    return json.dumps(responseDict)

@socket.on('relinquishmentRequest')
def relinquishment(sid, data):
    jsonData = json.loads(data)
    relinquishArr = []
    print("Relinquishment request received:")
    print(jsonData)
    for relinquishmentRequest in jsonData["relinquishmentRequest"]:
        print("Processing relinquishment request for CBSD: " + relinquishmentRequest["cbsdId"] + " and grant: " + relinquishmentRequest["grantId"])
        params = {}
        params["cbsdId"] = relinquishmentRequest["cbsdId"]
        params["grantId"] = relinquishmentRequest["grantId"]
        params["action"] = "relinquishGrant"
        if databaseLogging:
            sendPostRequest(params)
        success = None
        if (getGrantWithID(relinquishmentRequest["grantId"]) != None):
            success = removeGrant(getGrantWithID(relinquishmentRequest["grantId"]).id, relinquishmentRequest["cbsdId"])
        else:
            relinquishmentRequest["grantId"] = "Terminated"
        response = {}
        response["cbsdId"] = relinquishmentRequest["cbsdId"]
        response["grantId"] = relinquishmentRequest["grantId"]
        if relinquishmentRequest["cbsdId"] == None or relinquishmentRequest["grantId"] == None:
            response["response"] = generateResponse(102)
        elif success:
            response["response"] = generateResponse(0)
        elif relinquishmentRequest["grantId"] == "Terminated":
            response["response"] = generateResponse(501)
        else:
            response["response"] = generateResponse(103)
        relinquishArr.append(response)
        if success:
            for i, item in enumerate(SpectrumList):
                if(item['cbsdId'] == relinquishmentRequest['cbsdId']):
                    item['state'] = 1
                    item['stateText'] = "Registered"
                    SpectrumList[i] = item
            for i, cbsd in enumerate(CbsdList):
                if(cbsd['cbsdId'] == relinquishmentRequest['cbsdId']):
                    cbsd['state'] = 1
                    cbsd['stateText'] = "Registered"
                    CbsdList[i] = cbsd

    socket.emit('spectrumUpdate', SpectrumList)
    socket.emit('cbsdUpdate', CbsdList)
    responseDict = {"relinquishmentResponse":relinquishArr}
    socket.emit('relinquishmentResponse', to=sid, data=json.dumps(responseDict))
    return json.dumps(responseDict)

@socket.on('spectrumInquiryRequest')
def spectrumInquiryRequest(sid, data):
    jsonData = json.loads(data)
    inquiryArr = []
    for request in jsonData["spectrumInquiryRequest"]:
        response = WinnForum.SpectrumInquiryResponse(request["cbsdId"], [], SASAlgorithms.generateResponse(0))
        channelType = "GAA"
        for i, cbsd in enumerate(CbsdList):
                if(cbsd['cbsdId'] == request['cbsdId']):
                    channelType = cbsd['accessPriority']
        for fr in request["inquiredSpectrum"]:
            lowFreq = int(fr["lowFrequency"])
            highFreq = int(fr["highFrequency"])

            # channelType = "PAL"
            ruleApplied = "FCC_PART_96"
            maxEirp = SASAlgorithms.getMaxEIRP()
            if SASAlgorithms.acceptableRange(lowFreq, highFreq):
                # if highFreq < 3700000000 and highFreq > 3650000000:
                #     channelType = "GAA"
                present = SASAlgorithms.isPUPresentREM(REM, highFreq, lowFreq, None, None, None)
                print("Present =")
                print (REM.objects)
                present = 0
                if present == 0:#not present
                    fr = WinnForum.FrequencyRange(lowFreq, highFreq)
                    availChan = WinnForum.AvailableChannel(fr, channelType, ruleApplied, maxEirp)
                    response.availableChannel.append(availChan)
                elif present == 2:#no spectrum data
                    initiateSensing(lowFreq, highFreq)


        inquiryArr.append(response.asdict())
    responseDict = {"spectrumInquiryResponse":inquiryArr}
    socket.emit('spectrumInquiryResponse', json.dumps(responseDict))
    return json.dumps(responseDict)

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
        # Delete grant from list
        threading.Timer(1000, removeGrant, [grant.id, grant.cbsdId]).start()
        terminateGrant(grant.id, grant.cbsdId)
        print('grant ' + grant.id + ' canceled')
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

sensor_process = SensorProcessor()
sensor_list = []

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OpenSAS HTTPS server')

    def do_POST(self):
        if (self.path == "/sas-api/registration"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            sas_resp = register('', body)
            # response.write(b'This is POST request. ')
            # response.write(b'Received: ')
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
        if (self.path == "/sas-api/spectrumInquiry"):
            print("Spectrum Inquiry")
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            sas_resp = spectrumInquiryRequest('', body)
            # response.write(b'This is POST request. ')
            # response.write(b'Received: ')
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
        if (self.path == "/sas-api/grant"):
            print("Grant")
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            sas_resp = grantRequest('', body)
            # response.write(b'This is POST request. ')
            # response.write(b'Received: ')
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
        if (self.path == "/sas-api/heartbeat"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            sas_resp = heartbeat('', body)
            # response.write(b'This is POST request. ')
            # response.write(b'Received: ')
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
        if (self.path == "/sas-api/relinquishment"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            sas_resp = relinquishment('', body)
            # response.write(b'This is POST request. ')
            # response.write(b'Received: ')
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
        if (self.path == "/sas-api/deregistration"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            sas_resp = deregister('', body)
            # response.write(b'This is POST request. ')
            # response.write(b'Received: ')
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
        if self.path == "/sas-api/measurements":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            json_str = body.decode('utf-8')  # Decode the bytes into a string
            json_data = json.loads(json_str)  # Parse the string into a JSON object
            sas_resp = 'Received Measurements'
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
            # Set the flag to false
            SensorDataflag = False
            # Check if data from this sensor is already present
            for sensor in sensor_list:
                if sensor["sensor_id"] == json_data["sensor_id"]:
                    # If yes, iterate through channels and update the power with enumerate
                    for index, channel  in enumerate(sensor["channels"]):
                        channel["power"] = json_data["channels"][index]["power"]
                        channel["detected"] = json_data["channels"][index]["detected"]

                    # Set the flag to break the loop
                    SensorDataflag = True
                    break
            # If the sensor data is not present, add it to the list
            if SensorDataflag == False:
                sensor_list.append(json_data)
            # Create a JSON object to send to the client
            # print(sensor_list)

            # Send the data to the client
            socket.emit("sensorUpdate", data=sensor_list[0])

        if self.path == "/sas-api/samples":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            json_str = body.decode('utf-8')  # Decode the bytes into a string
            json_data = json.loads(json_str)  # Parse the string into a JSON object
            print(json_data.keys())
            # print(json_data['iq_samples'])

            prediction = sensor_process.processSensorData(json_data['iq_samples'], json_data['sensor_info'], json_data['detected_channel'])
            # Add the prediction to the sensor_list list
            if prediction is not None:
                for sensor in sensor_list:
                    if sensor["sensor_id"] == json_data["sensor_info"]["sensor_id"]:
                        # Iterate through the channels and update the prediction
                        for channel in sensor["channels"]:
                            if channel["id"] == json_data["detected_channel"]:
                                channel["prediction"] = prediction
                                incumbent_detected = False
                                if(prediction[0] >= 0.80):
                                    channel["signal"] = "Incumbent"
                                    incumbent_detected = True
                                if(prediction[0] <= 0.30):
                                    channel["signal"] = "unknown"
                                if(prediction[0] > 0.30 and prediction[0] < 0.80):
                                    channel["signal"] = "unknown"

                                # Call signalDetected() function
                                signalDetected(channel["id"], incumbent_detected, json_data["sensor_info"])
                    break
            sas_resp = 'Received IQ samples'
            print(sas_resp)
            response.write(str.encode(sas_resp))
            self.wfile.write(response.getvalue())
            socket.emit("sensorUpdate", data=sensor_list[0])

def thread2(args):
    # httpd = HTTPServer(('localhost', 1443), SimpleHTTPRequestHandler)
    # httpd.socket = ssl.wrap_socket (httpd.socket,
    #         keyfile="Certs/myCA.key",
    #         certfile='Certs/myCA.pem', server_side=True)
    # print("Listening on port 1443")
    # httpd.serve_forever()
    if(not isSimulating):
        threading.Timer(3.0, checkPUAlert).start()
    # eventlet.monkey_patch()
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

if __name__ == '__main__':
    getSettings()
    thread = Thread(target = thread2, args = (10, ))
    thread.start()
    # thread.join()
    # if(not isSimulating):
    #     threading.Timer(3.0, checkPUAlert).start()
    # eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
    httpd = HTTPServer(('0.0.0.0', 1443), SimpleHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket (httpd.socket,
           keyfile="Certs/server_10.147.20.75.key",
           certfile='Certs/server_10.147.20.75.crt', server_side=True)
    print("Listening on port 1443")
    httpd.serve_forever()

