from flask import request, jsonify, Blueprint, current_app
import database


app_routes = Blueprint('app_routes', __name__)
# TODO: Documentation and Swagger Implementation
#  [https://github.com/flasgger/flasgger]


def responseHandler(response):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    json_response = jsonify(response)
    json_response.headers.extend(headers)

    return json_response


def errorHandler(error):
    current_app.logger.exception(str(error))
    return responseHandler({"status": 0, "message": str(error)})

# --- USER REGISTRATION & ACCESS ROUTES ---


@app_routes.route('/suLogin', methods=['POST'])
def suLogin():
    requestBody = request.get_json()
    try:
        response = database.secondaryUserLogin(requestBody)
        return responseHandler(response)
    except Exception as e:
        return errorHandler(e)


@app_routes.route('/adminLogin', methods=['POST'])
def adminLogin():
    requestBody = request.get_json()
    try:
        response = database.adminLogin(requestBody)
        return responseHandler(response)
    except Exception as e:
        return errorHandler(e)


@app_routes.route('/createSU', methods=['POST'])
def createSU():
    requestBody = request.get_json()
    try:
        response = database.createSU(requestBody)
        return responseHandler(response)
    except Exception as e:
        return errorHandler(e)


@app_routes.route('/checkEmailAvail', methods=['POST'])
def checkEmailAvailability():
    requestBody = request.get_json()
    try:
        response = database.checkEmailAvailability(requestBody)
        return responseHandler(response)
    except Exception as e:
        return errorHandler(e)

# --- NODE MANAGEMENT ROUTES ---


@app_routes.route('/nodes', methods=['GET'])
def getNodes():
    try:
        response = database.getNodes()
        return responseHandler(response)
    except Exception as e:
        return errorHandler(e)


@app_routes.route('/createNode', methods=['POST'])
def createNode():
    requestBody = request.get_json()
    try:
        response = database.createNode(requestBody)
        return responseHandler(response)
    except Exception as e:
        return errorHandler(e)
