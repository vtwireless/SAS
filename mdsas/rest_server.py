"""
REST API Server for CCI-MDSAS

Created: Sept 20, 2022
Author/s: Saurav Kumar
Advised by Dr. Carl Dietrich (cdietric@vt.edu)
For Wireless@VT
"""
import json
import os
import threading
import time

from flask import Flask, request
import traceback
import logging
from datetime import datetime, timedelta, timezone

from algorithms import SASAlgorithms
from algorithms import SASREM
from controllers import DatabaseController
from settings import settings
from flask_cors import CORS

allClients = []
allRadios = []  # CBSDSocket
allWebApps = []
allSASs = []
grants = []
cbsds = []  # cbsd references
CbsdList = []
SpectrumList = []

databaseLogging = False
isSimulating = True
NUM_OF_CHANNELS = 15
puDetections = {}

DyanmicProtectionAreas = [
    {
        "id": "DPA-HCRO",
        "name": "HCRO",
        "latitude": 40.817132,
        "longitude": -121.470741,
        "radius": 200000,  # in metres
        "activationTime": "2023-03-25T05:55:00Z",
        "deactivationTime": "2023-03-25T08:10:00Z",
        "active": False,
        "spectrum": [[3550000000, 3590000000]]
    }
]

if settings.ENVIRONMENT == 'DEVELOPMENT':
    db = DatabaseController.DatabaseController(True)
else:
    db = DatabaseController.DatabaseController(False)

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()

server = Flask(settings.APP_NAME)
cors = CORS(server, resources={r"/*": {"origins": "*"}})

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
handler.setLevel(logging.INFO)
server.logger.handlers.clear()
server.logger.addHandler(handler)
server.logger.setLevel(logging.DEBUG)


@server.route('/', methods=['GET', 'POST'])
def root():
    return {"message": "Server is Running!"}


# In[ --- User Management ---]
@server.route('/suLogin', methods=['POST'])
def suLogin():
    """
    Login API for secondary users
    Returns User Information upon successful inquiry
    -------

    """
    try:
        response = db.authenticate_user(request.get_json(), False)
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/adminLogin', methods=['POST'])
def adminLogin():
    try:
        response = db.authenticate_user(request.get_json(), True)
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/createSU', methods=['POST'])
def createSecondaryUser():
    try:
        response = db.create_user(request.get_json(), False)
        return response

    except Exception as err:
        server.logger.debug(traceback.format_exc())
        return {
            'status': 0,
            'message': f"ErrorType: {err.__class__.__name__}, Message: {str(err)}"
        }


@server.route('/createAdminUserINsas', methods=['POST'])
def createAdminUser():
    try:
        response = db.create_user(request.get_json(), True)
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/getUsers', methods=['GET'])
def getSecondaryUsers():
    try:
        response = db.get_secondary_users()
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/getUser', methods=['POST'])
def getUser():
    try:
        response = db.get_secondary_user(request.get_json())
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/checkEmailAvail', methods=['POST'])
def checkEmailAvailability():
    try:
        response = db.check_email_availability(request.get_json())
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


# In[ --- Node Management ---]

@server.route('/getNodesRequest', methods=['GET'])
def getNodes():
    try:
        response = db.get_nodes()
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/registrationRequest', methods=['POST'])
def register():
    # response, assignmentArr = db.register_nodes(1, request.get_json())

    # TODO: Does dev server need a socket?
    # if the radio does not get the assignment out of the meas config
    # for radio in assignmentArr:
    #     sendAssignmentToRadio(radio)

    # return response

    try:
        response, assignmentArr = db.register_nodes(1, request.get_json())
        return response
    except Exception as err:
        print(traceback.format_exc())
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/deregistrationRequest', methods=['POST'])
def deregister():
    response = db.deregister_nodes(request.get_json())
    return response


@server.route('/updateNode', methods=['POST'])
def updateNode():
    try:
        response = db.update_nodes(request.get_json())
    except Exception as err:
        response = {'status': 0, 'message': str(err)}

    return response


# In[ --- Grant Management --- ]


@server.route('/spectrumInquiryRequest', methods=['POST'])
def spectrumInquiryRequest():
    try:
        response, radiosToCommunicate = db.spectrum_inquiry(request.get_json())

        # TODO: Does dev server need a socket?
        # for radio in radiosToCommunicate:
        #     socket.emit(
        #         "changeRadioParams", data=radio['data'], room=radio['room']
        #     )

        return response

    except Exception:
        return {
            'status': 0, 'message': traceback.format_exc()
        }


@server.route('/getSpectrumInquiryRequest', methods=['GET'])
def getSpectrumInquiryRequest():
    try:
        response = None
        return response

    except Exception:
        return {
            "status": 0, "message": traceback.format_exc()
        }


@server.route('/getGrantsRequest', methods=['GET'])
def getGrantRequests():
    try:
        response = db.get_grants()
        return response
    except Exception:
        return {
            'status': 0, 'message': traceback.format_exc()
        }


@server.route('/getSpectrumInquiries', methods=['GET'])
def getInquiryRequests():
    try:
        response = db.get_inquiries()
        return response
    except Exception:
        return {
            'status': 0, 'message': traceback.format_exc()
        }


@server.route('/grantRequest', methods=['POST'])
def grantRequest():
    try:
        response = db.create_grant_request(request.get_json())
        return response
    except Exception:
        return {
            'status': 0, 'message': traceback.format_exc()
        }


@server.route('/heartbeatRequest', methods=['POST'])
def heartbeat():
    response, grantArray = db.heartbeat_request(request.get_json())

    for grant in grantArray:
        threading.Timer(
            (grant.heartbeatInterval * 1.1) + 2, db.cancel_grant, [grant]
        ).start()

    return response


@server.route('/relinquishmentRequest', methods=['POST'])
def relinquishment():
    try:
        response = db.relinquishment_request(request.get_json())
        return response

    except Exception as err:
        print(traceback.format_exc())
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/deleteGrantRequest', methods=['POST'])
def deleteGrantRequest():
    try:
        response = db.delete_grant_by_id(request.get_json())
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


# In[ --- Tier Class Management ---]

@server.route('/getTierClassById', methods=['POST'])
def getTierClassById():
    try:
        response = db.get_tierclass_by_id(request.get_json())
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/getTierClass', methods=['GET'])
def getTierClass():
    try:
        response = db.get_tierclass()
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/createTierClass', methods=['POST'])
def createTierClass():
    try:
        response = db.create_tierclass(request.get_json())
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


###############################################################################################################################


################################################# Dynamic Protected Areas #####################################################
def terminateGrant(grantId, cbsdId):
    for g in grants:
        if str(g.id) == str(grantId) and str(g.cbsdId) == str(cbsdId):
            print("Terminating grant: " + str(grantId) + " from CBSD: " + str(cbsdId) + " from list")
            g.status = "TERMINATED"
            return True
    return False


# Function that checks if dynamic protection areas startTime are approaching and if so, activate them
def checkDynamicProtectionAreas():
    while True:
        print("Checking dynamic protection areas")
        for area in DyanmicProtectionAreas:
            if area["active"] == False:
                if datetime.now(timezone.utc) > datetime.fromisoformat(area["activationTime"].replace('Z', '+00:00')):
                    # Check if the deactivation time is in the past
                    if datetime.now(timezone.utc) > datetime.fromisoformat(
                            area["deactivationTime"].replace('Z', '+00:00')):
                        continue
                    area["active"] = True
                    print("Activating dynamic protection area " + area["id"] + "...")
                    DpaGrant = SASAlgorithms.createDPAGrant(area, grants, CbsdList, SpectrumList)
                    grants.append(DpaGrant)
                    # socket.emit('dpaUpdate', DyanmicProtectionAreas)
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
                                # socket.emit('dpaUpdate', DyanmicProtectionAreas)
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
                                deactivation_time = datetime.fromisoformat(
                                    dpa_object["deactivationTime"].replace("Z", "+00:00"))
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
                        distance = SASAlgorithms.calculateDistance((area["latitude"], area["longitude"]),
                                                                   (DPA["latitude"], DPA["longitude"]))
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


# # Thread to check if new DPA reservation requests are available
# thread = threading.Thread(target=checkReservationRequests)
# thread.start()
#
# # Thread to check if dynamic protection areas are approaching
# thread = threading.Thread(target=checkDynamicProtectionAreas)
# time.sleep(5)
# thread.start()

################################################################################################################################################


# In[ --- Main ---]
if __name__ == "__main__":
    # uvicorn.run(server, host="0.0.0.0", port=8000)
    # server.run(host='0.0.0.0', port=8000)
    server.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=False,
        ssl_context=('certs/server.crt', 'certs/server.key')
    )
