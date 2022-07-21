import sqlalchemy as db
from sqlalchemy.engine import CursorResult

import settings
import os


class DatabaseController:
    ENGINE = None
    CONNECTION = None
    METADATA = None
    SU_TABLE = None

    def __init__(self):
        self.delete_db_file()

        if settings.ENVIRONMENT == 'DEVELOPMENT':
            self.connect_to_dev_db()
        else:
            self.connect_to_prod_db()

        # Initialize tables
        self.create_tables()

        # Create Admin User
        admin_user = {
            'secondaryUserName': settings.ADMIN_EMAIL,
            'secondaryUserEmail': settings.ADMIN_EMAIL,
            'secondaryUserPassword': settings.ADMIN_PWD,
            'deviceID': '',
            'location': ''
        }
        self.user_creation(admin_user, True)

    def connect_to_dev_db(self):
        self.ENGINE = db.create_engine(settings.DEVELOPMENT_DATABASE_URI)
        self.CONNECTION = self.ENGINE.connect()
        self.METADATA = db.MetaData()

    def connect_to_prod_db(self):
        self.ENGINE = db.create_engine(settings.PRODUCTION_DATABASE_URI)
        self.CONNECTION = self.ENGINE.connect()
        self.METADATA = db.MetaData()

    def execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def delete_table(self, table: db.Table):
        table.drop(self.ENGINE)

    def delete_all_tables(self):
        self.METADATA.drop_all(self.ENGINE)

    @staticmethod
    def delete_db_file():
        try:
            os.remove(settings.SQLITE_FILE)
        except Exception as exception:
            print(str(exception))

    def disconnect_from_db(self):
        self.CONNECTION.close()
        self.delete_db_file()

    # ################ CREATE TABLES ################
    def create_tables(self):
        self.set_secondaryUser_table()

    def set_secondaryUser_table(self):
        secondaryUser = db.Table(
            settings.SECONDARY_USER_TABLE, self.METADATA,
            db.Column('username', db.String(80), nullable=False),
            db.Column('email', db.String(80), index=True, unique=True, nullable=False, primary_key=True),
            db.Column('admin', db.Boolean, nullable=False),
            db.Column('password', db.String(80), nullable=False),
            db.Column('deviceID', db.String(80), nullable=False),
            db.Column('location', db.String(80), nullable=False)
        )

        self.METADATA.create_all(self.ENGINE)
        self.SU_TABLE = db.Table(
            settings.SECONDARY_USER_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    # ################ DATABASE CONTROLS ################
    def user_authentication(self, payload: any, isAdmin: bool):
        email = payload['username']
        password = payload['password']

        if not email or not password:
            raise Exception("Username or password not provided")

        query = db.select([self.SU_TABLE]).where(db.and_(
            self.SU_TABLE.columns.email == email,
            self.SU_TABLE.columns.password == password,
            self.SU_TABLE.columns.admin == isAdmin
        ))
        rows = self.execute_query(query)

        if len(rows) < 1:
            return {
                "status": 0
            }

        return {
            "status": 1,
            "name": rows[0]['username'],
            "id": rows[0]['username'],
            "userType": 'SU' if not rows[0]['admin'] else 'ADMIN'
        }

    def user_creation(self, payload, isAdmin):
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

        query = db.select([self.SU_TABLE]).where(self.SU_TABLE.columns.email == email)
        rows = self.execute_query(query)
        if len(rows) > 0:
            message = f"Email '{email}' already exists. Contact an administrator to recover or reset password."
            return {
                "status": 0,
                "exists": 1,
                "message": message
            }

        insert = db.insert(self.SU_TABLE).values(
            username=username, email=email, admin=isAdmin, password=password, deviceID=deviceID, location=location
        )
        ResultProxy = self.CONNECTION.execute(insert)

        rows = self.execute_query(query)
        if len(rows) < 1:
            return {
                "status": 0,
                "message": "User could not be added. Contact an administrator."
            }

        return {
            "status": 1,
            "message": "User has been added."
        }


