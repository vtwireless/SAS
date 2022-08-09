from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.GRANTLOG, metadata,
        Column('grantLogID', Integer, primary_key=True, autoincrement=True),
        Column('approved', Boolean, index=False, unique=False, nullable=False, default=False),
        Column('secondaryUserID', String(80), index=False, unique=False, nullable=False, default=''),
        Column('frequency', Float, index=False, unique=False, nullable=False, default=0),
        Column('bandwidth', Float, index=False, unique=False, nullable=False, default=0),
        Column('startTime', String(80), index=False, unique=False, nullable=False, default=''),
        Column('endTime', String(80), index=False, unique=False, nullable=False, default=''),
        Column('status', String(80), index=False, unique=False, nullable=False, default=''),
        Column('requestMinFrequency', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestMaxFrequency', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestPreferredFrequency', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestFrequencyAbsolute', Boolean, index=False, unique=False, nullable=False, default=False),
        Column('minBandwidth', Float, index=False, unique=False, nullable=False, default=0),
        Column('preferredBandwidth', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestStartTime', String(80), index=False, unique=False, nullable=False, default=''),
        Column('requestEndTime', String(80), index=False, unique=False, nullable=False, default=''),
        Column('requestApproximateByteSize', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestDataType', String(80), index=False, unique=False, nullable=False, default=''),
        Column('requestPowerLevel', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestLocation', String(80), index=False, unique=False, nullable=False, default=''),
        Column('requestMobility', Boolean, index=False, unique=False, nullable=False, default=False),
        Column('requestMaxVelocity', Float, index=False, unique=False, nullable=False, default=0)
    )
