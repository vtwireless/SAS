from sqlalchemy import Column, String, Boolean, Integer, Float, SmallInteger
from sqlalchemy import MetaData, Table

import settings


class Schemas:
    def __init__(self, metadata: MetaData):
        self._metadata = metadata

    def create_tables(self):
        self.__get_user_table()
        self.__get_node_table()
        self.__get_grant_table()
        
    def __get_user_table(self):
        Table(
            settings.SECONDARY_USER_TABLE, self._metadata,
            Column('username', String(80), nullable=False),
            Column('email', String(80), index=True, unique=True, nullable=False, primary_key=True),
            Column('admin', Boolean, nullable=False),
            Column('password', String(80), nullable=False),
            Column('deviceID', String(80), nullable=False),
            Column('location', String(80), nullable=False)
        )

    def __get_node_table(self):
        Table(
            settings.NODE_TABLE, self._metadata,
            Column('nodeID', Integer, primary_key=True),
            Column('fccId', String(80), index=False, unique=False, nullable=False),
            Column('nodeName', String(80), index=False, unique=False, nullable=False),
            Column('location', String(80), index=False, unique=False, nullable=False, default=''),
            Column('trustLevel', Integer, index=False, unique=False, nullable=False),
            Column('IPAddress', String(80), index=False, unique=False, nullable=False),
            Column('minFrequency', Float, index=False, unique=False, nullable=False),
            Column('maxFrequency', Float, index=False, unique=False, nullable=False),
            Column('minSampleRate', Float, index=False, unique=False, nullable=False),
            Column('maxSampleRate', Float, index=False, unique=False, nullable=False),
            Column('nodeType', String(80), index=False, unique=False, nullable=False),
            Column('mobility', SmallInteger, index=False, unique=False, nullable=False),
            Column('status', String(80), index=False, unique=False, nullable=False),
            Column('userId', String(80), index=False, unique=False, nullable=False, default=''),
            Column('cbsdSerialNumber', String(80), index=False, unique=False, nullable=False, default=''),
            Column('cbsdCategory', String(80), index=False, unique=False, nullable=False, default=''),
            Column('cbsdInfo', String(80), index=False, unique=False, nullable=False, default=''),
            Column('callSign', String(80), index=False, unique=False, nullable=False, default=''),
            Column('airInterface', String(80), index=False, unique=False, nullable=False, default=''),
            Column('installationParam', String(80), index=False, unique=False, nullable=False, default=''),
            Column('measCapability', String(80), index=False, unique=False, nullable=False, default=''),
            Column('groupingParam', String(80), index=False, unique=False, nullable=False, default=''),
            Column('fullyTrusted', String(80), index=False, unique=False, nullable=False, default=''),
            Column('comment', String(80), index=False, unique=False, nullable=False)
        )

    def __get_grant_table(self):
        Table(
            settings.GRANT_TABLE, self._metadata,
            Column('requestID', Integer, primary_key=True),
            Column('secondaryUserID', String(80), index=False, unique=False, nullable=''),
            Column('secondaryUserName', String(80), index=False, unique=False, nullable='', default=''),
            Column('tier', String(80), index=False, unique=False, nullable='', default=''),
            Column('minFrequency', Float, index=False, unique=False, nullable=False),
            Column('maxFrequency', Float, index=False, unique=False, nullable=False),
            Column('preferredFrequency', Float, index=False, unique=False, nullable=False),
            Column('frequencyAbsolute', Boolean, index=False, unique=False, nullable=False),
            Column('minBandwidth', Float, index=False, unique=False, nullable=False),
            Column('preferredBandwidth', Float, index=False, unique=False, nullable=False),
            Column('startTime', String(80), index=False, unique=False, nullable=''),
            Column('endTime', String(80), index=False, unique=False, nullable=''),
            Column('approximateByteSize', Float, index=False, unique=False, nullable=''),
            Column('dataType', String(80), index=False, unique=False, nullable=''),
            Column('powerLevel', Float, index=False, unique=False, nullable=''),
            Column('location', String(80), index=False, unique=False, nullable='', default=''),
            Column('mobility', Boolean, index=False, unique=False, nullable=''),
            Column('maxVelocity', String(80), index=False, unique=False, nullable=''),
            Column('range', String(80), index=False, unique=False, nullable='', default='')
        )
