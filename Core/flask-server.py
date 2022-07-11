from flask import Flask, json, request, jsonify
from flask_cors import CORS
import database

app = Flask(__name__)
CORS(app)


def responseHandler(response):
    json_response = jsonify(response)
    json_response.headers.add('Access-Control-Allow-Origin', '*')
    return json_response


############################ ROUTES ######################################


@app.route('/suLogin', methods=['POST'])
def suLogin():
    requestBody = request.get_json()
    print("req body", requestBody)
    try:
        response = database.secondaryUserLogin(requestBody)
        return responseHandler(response)
    except Exception as e:
        print(e)
        return responseHandler({"message": str(e)})


@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    requestBody = request.get_json()
    print("req body", requestBody)
    try:
        response = database.adminLogin(requestBody)
        return responseHandler(response)
    except Exception as e:
        print(e)
        return responseHandler({"message": str(e)})


@app.route('/nodes', methods=['GET'])
def getNodes():
    try:
        response = database.getNodes()
        return responseHandler(response)
    except Exception as e:
        print(e)
        return responseHandler({"message": str(e)})

##########################################################################


if __name__ == '__main__':
    app.run('localhost', 8000)
