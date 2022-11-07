import sqlalchemy as db
from sqlalchemy import select, and_, insert
from sqlalchemy.engine import CursorResult

from settings import settings


class UsersController:
    USERS = None

    def __init__(self, metadata, engine, connection, algorithms):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms = algorithms

        self._set_secondaryUser_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def _set_secondaryUser_table(self):
        self.USERS = db.Table(
            settings.SECONDARY_USER_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

        # Create Admin User
        admin_user = {
            'secondaryUserName': settings.ADMIN_EMAIL,
            'secondaryUserEmail': settings.ADMIN_EMAIL,
            'secondaryUserPassword': settings.ADMIN_PWD,
            'deviceID': '',
            'location': ''
        }
        self.create_user(admin_user, True)

    def get_secondary_users(self):
        query = select([self.USERS])
        rows = self._execute_query(query)

        return {
            'status': 1,
            'secondaryUsers': rows
        }

    def get_secondary_user(self, payload):
        email = payload['username']
        password = payload['password']

        query = select([self.USERS]).where(and_(
            self.USERS.columns.email == email,
            self.USERS.columns.password == password
        ))

        rows = self._execute_query(query)

        return {
            'status': 1,
            'user': rows
        }

    def authenticate_user(self, payload: any, isAdmin: bool):
        email = payload.get('username', None)
        password = payload.get('password', None)

        if not email or not password:
            raise Exception("Username or password not provided")

        query = select([self.USERS]).where(and_(
            self.USERS.columns.email == email,
            self.USERS.columns.password == password,
            self.USERS.columns.admin == isAdmin
        ))
        rows = self._execute_query(query)

        if len(rows) < 1:
            return {
                "status": 0,
                'message': "User could not be found"
            }

        return {
            "status": 1,
            "name": rows[0]['username'],
            "id": rows[0]['username'],
            "userType": 'SU' if not rows[0]['admin'] else 'ADMIN'
        }

    def create_user(self, payload, isAdmin):
        username = payload['secondaryUserName']
        email = payload['secondaryUserEmail']
        password = payload['secondaryUserPassword']
        deviceID = payload['deviceID']
        location = payload['location']

        # Sanity Checks
        if not username:
            raise Exception("Username not provided")

        if not email:
            raise Exception("Email Address not provided")

        if not password:
            raise Exception("Password not provided")

        query = select([self.USERS]).where(self.USERS.columns.email == email)
        rows = self._execute_query(query)
        if len(rows) > 0:
            message = f"Email '{email}' already exists. Contact an administrator to recover or reset password."
            return {
                "status": 0,
                "exists": 1,
                "message": message
            }

        insertQuery = insert(self.USERS).values(
            username=username, email=email, admin=isAdmin, password=password, deviceID=deviceID, location=location
        )
        ResultProxy = self.CONNECTION.execute(insertQuery)

        rows = self._execute_query(query)
        if len(rows) < 1:
            return {
                "status": 0,
                "message": "User could not be added. Contact an administrator."
            }

        return {
            "status": 1,
            "message": "User has been added."
        }

    def check_email_availability(self, payload):
        email = payload.get('email', None)

        if not email:
            raise Exception("Email not provided")

        query = select([self.USERS]).where(
            self.USERS.columns.email == email
        )

        rows = self._execute_query(query)

        if len(rows) > 1:
            return {
                'status': 1,
                'exists': 1,
                'message': 'Email In Use'
            }
        return {
            'status': 1,
            'exists': 0,
            'message': 'Email Unique'
        }

    def load_seed_data(self):
        self.create_user(
            self.generate_seed_payload('abc', 'abc@abc.com', 'password', '100.121.1.15', '35.6673,-81.5411'), False
        )
        self.create_user(
            self.generate_seed_payload('bbc', 'bbc@abc.com', 'password', '100.121.1.16', '36.6673,-85.5411'), False
        )
        self.create_user(
            self.generate_seed_payload('cbc', 'cbc@abc.com', 'password', '100.121.1.17', '39.6673,-89.5411'), False
        )

    @staticmethod
    def generate_seed_payload(name, email, password, deviceId, location):
        return {
            'secondaryUserName': name,
            'secondaryUserEmail': email,
            'secondaryUserPassword': password,
            'deviceID': deviceId,
            'location': location
        }
