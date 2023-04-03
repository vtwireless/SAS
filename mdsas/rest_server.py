"""
REST API Server for CCI-MDSAS

Created: Sept 20, 2022
Author/s: Saurav Kumar
Advised by Dr. Carl Dietrich (cdietric@vt.edu)
For Wireless@VT
"""
import threading
from flask import Flask, request
import traceback
import logging
import sys

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

databaseLogging = False
isSimulating = True
NUM_OF_CHANNELS = 15
puDetections = {}

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


# In[ --- Base Station Management ---]

@server.route('/getBaseStations', methods=['GET'])
def getBaseStations():
    try:
        response = db.get_base_station()
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/registerBaseStations', methods=['POST'])
def registerBaseStations():
    try:
        response = db.register_base_stations(request.get_json())
        return response
    except Exception as err:
        print(traceback.format_exc())
        return {
            'status': 0, 'message': str(err)
        }


@server.route('/updateBaseStationStatus', methods=['POST'])
def updateBSStatus():
    try:
        response = db.change_base_station_status(request.get_json())
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
