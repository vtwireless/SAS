import MySQLdb
from MySQLdb.cursors import DictCursor

# Define DB params TODO: Move to a config file
HOST = "localhost"
USER = "root"
PASSWORD = "root"
DATABASE = "spectrumGrant"

USERTABLE = "secondaryuser"
ADMINTABLE = "admin"
NODETABLE = "node"

# TODO: Database connection object should be created once and then supplied elsewhere. In the current
#  implementation, a new connection object is getting created everytime database.py is executed. Due
#  to this, if DB is updated via CLI we don't see changes in UI until FLASK is restarted.
dbconnect = MySQLdb.connect(HOST, USER, PASSWORD, DATABASE)
dbcursor = dbconnect.cursor(cursorclass=DictCursor)

# --- HELPER

def formatReturnable(status, payload):
    if status == 0:
        return {
            'status': 0
        }
    else:
        payload['status'] = 1
        return payload


def checkIfExists(tableName, args: dict):
    if not args:
        return False

    args_list = ["=".join([key, f"'{value}'"]) for key, value in args.items()]
    query = f"SELECT * FROM {tableName} WHERE " + " AND ".join(args_list)

    dbcursor.execute(query)
    queryResults = dbcursor.fetchone()

    if queryResults:
        return True

    return False


# --- USER REGISTRATION & ACCESS FUNCTIONALITIES ---


def secondaryUserLogin(payload):
    username = payload['username']
    password = payload['password']

    if not username or not password:
        raise Exception("Username or password not provided")

    query = f"SELECT *  FROM {USERTABLE} WHERE secondaryUserEmail = '{username}' AND secondaryUserPassword = '{password}'"
    dbcursor.execute(query)
    queryResults = list(dbcursor.fetchall())

    if len(queryResults) < 1:
        return formatReturnable(0, {})
    else:
        response = {
            'id': queryResults[0]['secondaryUserID'],
            'userType': 'SU',
            'name': queryResults[0]['secondaryUserName']
        }
        return formatReturnable(1, response)


def adminLogin(payload):
    username = payload['username']
    password = payload['password']

    if not username or not password:
        raise Exception("Username or password not provided")

    query = f"SELECT *  FROM {ADMINTABLE} WHERE adminEmail = '{username}' AND adminPassword = '{password}'"
    dbcursor.execute(query)
    queryResults = list(dbcursor.fetchall())

    if len(queryResults) < 1:
        return formatReturnable(0, {})
    else:
        response = {
            'id': queryResults[0]['adminID'],
            'userType': 'ADMIN',
            'name': queryResults[0]['adminName']
        }
        return formatReturnable(1, response)


def createSU(payload):
    secondaryUserName = payload['secondaryUserName']
    secondaryUserEmail = payload['secondaryUserEmail']
    secondaryUserPassword = payload['secondaryUserPassword']
    deviceID = payload['deviceID']
    location = payload['location']

    # Sanity Checks
    if not secondaryUserName:
        raise Exception("Username not provided")

    if not secondaryUserEmail:
        raise Exception("Email Address not provided")

    if not secondaryUserPassword:
        raise Exception("Password not provided")

    if checkIfExists(USERTABLE, {'secondaryUserEmail': secondaryUserEmail}):
        message = f"Email '{secondaryUserEmail}' already exists. Contact an administrator to recover or reset password."
        return formatReturnable(0, {"exists": 1, "message":message})

    # Create User
    query = f"INSERT INTO {USERTABLE} (secondaryUserEmail, secondaryUserPassword, secondaryUserName, deviceID, " \
            f"location, tier) VALUES ('{secondaryUserEmail}', '{secondaryUserPassword}', '{secondaryUserName}', " \
            f"'{deviceID}', '{location}', '3');"
    dbcursor.execute(query)
    dbconnect.commit()

    if not checkIfExists(USERTABLE, {'secondaryUserEmail': secondaryUserEmail}):
        message = "Secondary User could not be added. Contact an administrator."
        return formatReturnable(0, {"message": message})

    return formatReturnable(1, {"message": "Secondary User has been added."})


def checkEmailAvailability(payload):
    email = payload['email']

    if not email:
        raise Exception('Email Address not provided')

    if checkIfExists(USERTABLE, {"secondaryUserEmail": email}):
        return formatReturnable(1, {"exists": 1, "message": "Email Address already in use."})

    return formatReturnable(1, {"exists": 0, "message": "Email Address not in use."})

# --- NODE MANAGEMENT ROUTES ---

def getNodes():
    query = f'SELECT * FROM {NODETABLE}'
    dbcursor.execute(query)
    queryResults = list(dbcursor.fetchall())
    print(queryResults)

    return formatReturnable(1, {
        'nodes': queryResults
    })

def createNode(payload):
    nodeName = payload.get('nodeName', '')
    location = payload.get('location', '')
    SUID = payload.get('SUID', '')
    trustLevel = int(payload.get('trustLevel', '5'))
    IPAddress = payload.get('IPAddress', '')
    minFrequency = float(payload.get('minFrequency', '0'))
    maxFrequency = float(payload.get('maxFrequency', '0'))
    minSampleRate = float(payload.get('minSampleRate', '0'))
    maxSampleRate = float(payload.get('maxSampleRate', '0'))
    nodeType = payload.get('nodeType', '')
    status = payload.get('status', '')
    comment = payload.get('comment', '')
    mobility = payload.get('mobility', 'False').lower()
    if mobility == 'false':
        mobility = 0
    else:
        mobility = 1

    userId = payload.get('userId', '')
    fccId = payload.get('fccId', '')
    cbsdSerialNumber = payload.get('cbsdSerialNumber', '')
    callSign = payload.get('callSign', '')
    cbsdCategory = payload.get('cbsdCategory', '')
    cbsdInfo = payload.get('cbsdInfo', '')
    airInterface = payload.get('airInterface', '')
    installationParam = payload.get('installationParam', '')
    measCapability = payload.get('measCapability', '')
    groupingParam = payload.get('groupingParam', '')

    # Sanity Check
    if checkIfExists(NODETABLE, {'nodeName': nodeName}):
        message = "A node already exists with the same name"
        return formatReturnable(0, {"exists": 1, "message":message})

    # Create Node
    # TODO: Extra Params are currently missing from implementation
    # query = f"INSERT INTO {NODETABLE} (nodeName, secondaryUserId, location, trustLevel, IPAddress, minFrequency, " \
    #         f"maxFrequency, minSampleRate, maxSampleRate, nodeType, mobility, status, comment, fccId, " \
    #         f"cbsdSerialNumber, callSign, cbsdCategory, cbsdInfo, airInterface, installationParam, measCapability, " \
    #         f"groupingParam) VALUES ('{nodeName}', '{SUID}', '{location}', '{trustLevel}', '{IPAddress}', " \
    #         f"'{minFrequency}', '{maxFrequency}', '{minSampleRate}', '{maxSampleRate}', '{nodeType}', '{mobility}', " \
    #         f"'{status}', '{comment}', '{fccId}', '{cbsdSerialNumber}', '{callSign}', '{cbsdCategory}', '{cbsdInfo}'," \
    #         f" '{airInterface}', '{installationParam}', '{measCapability}', '{groupingParam}');"

    query = f"INSERT INTO {NODETABLE} (nodeName, location, trustLevel, IPAddress, minFrequency, maxFrequency, " \
            f"minSampleRate, maxSampleRate, nodeType, mobility, status, comment) VALUES ('{nodeName}', '{location}'," \
            f" '{trustLevel}', '{IPAddress}', '{minFrequency}', '{maxFrequency}', '{minSampleRate}', " \
            f"'{maxSampleRate}', '{nodeType}', '{mobility}', '{status}', '{comment}');"

    dbcursor.execute(query)
    dbconnect.commit()

    if not checkIfExists(NODETABLE, {'nodeName': nodeName}):
        message = "Node could not be added. Contact an administrator."
        return formatReturnable(0, {"message": message})

    return formatReturnable(1, {"message": "Node has been added."})

