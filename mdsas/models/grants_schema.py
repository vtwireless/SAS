from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.GRANT_TABLE, metadata,
        Column('requestID', Integer, primary_key=True, autoincrement=True),
        Column('grantId', Integer, autoincrement=True),
        Column('secondaryUserID', String(80), index=False, unique=False, nullable=False, default=''),
        Column('secondaryUserName', String(80), index=False, unique=False, nullable=False, default=''),
        Column('tier', String(80), index=False, unique=False, nullable=False, default=''),
        Column('minFrequency', Float, index=False, unique=False, nullable=False),
        Column('maxFrequency', Float, index=False, unique=False, nullable=False),
        Column('preferredFrequency', Float, index=False, unique=False, nullable=False),
        Column('frequencyAbsolute', Boolean, index=False, unique=False, nullable=False),
        Column('minBandwidth', Float, index=False, unique=False, nullable=False),
        Column('preferredBandwidth', Float, index=False, unique=False, nullable=False),
        Column('startTime', String(80), index=False, unique=False, nullable=False),
        Column('endTime', String(80), index=False, unique=False, nullable=False),
        Column('approximateByteSize', Float, index=False, unique=False, nullable=False),
        Column('dataType', String(80), index=False, unique=False, nullable=False),
        Column('powerLevel', Float, index=False, unique=False, nullable=False),
        Column('location', String(80), index=False, unique=False, nullable=False, default=''),
        Column('mobility', Boolean, index=False, unique=False, nullable=False),
        Column('maxVelocity', String(80), index=False, unique=False, nullable=False),
        Column('range', String(80), index=False, unique=False, nullable=False, default=''),
        Column('cbsdId', String(80), index=False, unique=True, nullable=False, default='')
    )
