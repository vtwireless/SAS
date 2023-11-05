"""
Very similar to server.py

Revised: Aug 8, 2022
Authored by: Saurav Kumar (sauravk3@vt.edu), Cameron Makin (cammakin8@vt.edu), Joseph Tolley (jtolley@vt.edu)
Advised by Dr. Carl Dietrich (cdietric@vt.edu)
For Wireless@VT
"""

import threading
import time
import eventlet
import socketio

from controllers import DatabaseController
from algorithms import SASAlgorithms
from algorithms import SASREM
from Utilities import Utilities
from settings import settings

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

if settings.ENVIRONMENT == 'DEVELOPMENT':
    db = DatabaseController.DatabaseController(True)
else:
    db = DatabaseController.DatabaseController(False)

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()


# In[ --- Connection Management ---]

@socket.event
def connect(sid, environ):
    print('connect ', sid)
    allClients.append(sid)


@socket.event
def disconnect(sid):
    print('disconnect ', sid)
    allClients.remove(sid)
    if sid in allWebApps:
        allWebApps.remove(sid)
    if sid in allSASs:
        allSASs.remove(sid)
    for radio in allRadios:
        if radio.sid == sid:
            allRadios.remove(radio)


# In[ --- User Management ---]

@socket.on('suLogin')
def suLogin(sid, data):
    try:
        response = db.authenticate_user(data, False)
        socket.emit('suLoginResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('suLoginResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('adminLogin')
def adminLogin(sid, data):
    try:
        response = db.authenticate_user(data, True)
        socket.emit('adminLoginResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('adminLoginResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('createSU')
def createSecondaryUser(sid, data):
    try:
        response = db.create_user(data, False)
        socket.emit('createSUResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('createSUResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('createAdminUserINsas')
def createAdminUser(sid, data):

    try:
        response = db.create_user(data, True)
        socket.emit('createAdminUserINsasResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('createAdminUserINsasResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('getUsers')
def getSecondaryUsers(sid, data):
    try:
        response = db.get_secondary_users()
        socket.emit('getUsersResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('getUsersResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('getUser')
def getUser(sid, data):
    try:
        response = db.get_secondary_user(data)
        socket.emit('getUserResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('getUserResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('checkEmailAvail')
def checkEmailAvailability(sid, data):
    try:
        response = db.check_email_availability(data)
        socket.emit('checkEmailResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('checkEmailResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


# In[ --- Tier Class Management ---]

@socket.on('getTierClassById')
def getTierClassById(sid, data):
    try:
        response = db.get_tierclass_by_id(data)
        socket.emit('getTierClassByIdResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('getTierClassByIdResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('getTierClass')
def getTierClass(sid, data):
    try:
        response = db.get_tierclass()
        socket.emit('getTierClassResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('getTierClassResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('createTierClass')
def createTierClass(sid, data):
    try:
        response = db.create_tierclass(data)
        socket.emit('createTierClassResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('createTierClassResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('updateTierClass')
def updateTierClass(sid, data):
    try:
        response = db.update_tierclass(data)
        socket.emit('updateTierClassResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('updateTierClassResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


# In[ --- Region Schedule Management ---]

@socket.on('createRegionSchedule')
def createRegionSchedule(sid, data):
    try:
        response = db.create_region_schedule(data)
        socket.emit('createRegionScheduleResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('createRegionScheduleResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


@socket.on('updateRegionSchedule')
def updateRegionSchedule(sid, data):
    try:
        response = db.update_region_schedule(data)
        socket.emit('updateRegionScheduleResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('updateRegionScheduleResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


# In[ --- Node Management ---]

@socket.on('getNodesRequest')
def getNodes(sid, payload):
    try:
        response = db.get_nodes()
        socket.emit('getNodesResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('getNodesResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


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


@socket.on('updateNode')
def updateNode(sid, payload):
    try:
        response = db.update_nodes(payload)
    except Exception as err:
        response = {'status': 0, 'message': str(err)}

    socket.emit('updateNodeResponse', to=sid, data=response)


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


# @socket.on('logGrant')
# def logGrant(sid, data):
#     try:
#         response = db.log_grant(data)
#         socket.emit('logGrantResponse', to=sid, data=response)
#
#     except Exception as err:
#         socket.emit('logGrantResponse', to=sid, data={
#             'status': 0, 'message': str(err)
#         })


@socket.on('deleteGrantRequest')
def deleteGrantRequest(sid, data):
    try:
        response = db.delete_grant_by_id(data)
        socket.emit('deleteGrantResponse', to=sid, data=response)

    except Exception as err:
        socket.emit('deleteGrantResponse', to=sid, data={
            'status': 0, 'message': str(err)
        })


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
    db.update_sas_settings(data)


@socket.on('spectrumData')
def spectrumData(sid, data):
    db.spectrumData(data)


@socket.on('incumbentInformation')
def incumbentInformation(sid, data):
    """Function for PUs to send their operating data"""
    obfuscated = db.incumbentInformation(data)

    for obs in obfuscated:
        sendObstructionToRadio(
            obs[0], obs[1], obs[2]
        )


# In[ --- TODO --- ]


def sendAssignmentToRadio(cbsd):
    # TODO: Refactor
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

    threading.Timer(3.0, Utilities.resetRadioStatuses, [[cbsd]]).start()


def sendObstructionToRadio(cbsd, lowFreq, highFreq):
    changeParams = {
        "lowFrequency": lowFreq,
        "highFrequency": highFreq,
        "cbsdId": cbsd.cbsdId
    }

    socket.emit(
        "obstructChannelWithRadioParams", changeParams, room=cbsd.sid
    )


def checkPUAlert(data=None):
    report, pauseArr = db.check_pudetections(data)
    for item in pauseArr:
        socket.emit('pauseGrant', to=item['sid'], data={'grantId': item['grantId']})

    # TODO: Check if we need to return anything
    # return report

    threading.Timer(1, checkPUAlert).start()


# In[ --- main --- ]

if __name__ == '__main__':
    if not isSimulating:
        threading.Timer(3.0, checkPUAlert).start()

    # TODO: move to gunicorn
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
