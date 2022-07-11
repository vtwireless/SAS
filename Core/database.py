import MySQLdb
from MySQLdb.cursors import DictCursor

# Define DB params TODO: Move to a config file
HOST = "localhost"
USER = "root"
PASSWORD = "root"
DATABASE = "spectrumGrant"

# Define Tables
SULOGIN = "secondaryuser"
ADMINLOGIN = "admin"
NODES = "node"

dbconnect = MySQLdb.connect(
    HOST,
    USER,
    PASSWORD,
    DATABASE
)

dbcursor = dbconnect.cursor(cursorclass=DictCursor)


def formatReturnable(status, payload):
    if status == 0:
        return {
            'status': 0
        }
    else:
        payload['status'] = 1
        return payload


def secondaryUserLogin(payload):
    username = payload['username']
    password = payload['password']

    if not username or not password:
        raise Exception("Username or password not provided")

    query = f"SELECT *  FROM {SULOGIN} WHERE secondaryUserEmail = '{username}' AND secondaryUserPassword = '{password}'"
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

    query = f"SELECT *  FROM {ADMINLOGIN} WHERE adminEmail = '{username}' AND adminPassword = '{password}'"
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


def getNodes():
    query = f'SELECT * FROM {NODES}'
    dbcursor.execute(query)
    queryResults = list(dbcursor.fetchall())

    return formatReturnable(1, {
        'nodes': queryResults
    })


# TODO: Only for testing. Remove thereafter.
if __name__ == '__main__':
    # Login Functionality
    loginPayload = {
        'username': "fake@fake",
        'password': "pass"
    }
    print(secondaryUserLogin(loginPayload))

