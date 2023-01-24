from sqlalchemy import Column, String, Integer, Float, SmallInteger, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.CBSD_TABLE, metadata,
        Column('cbsdID', Integer, primary_key=True, autoincrement=True),
        Column('fccId', String(80), index=False, unique=False, nullable=False, default=''),
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
        Column('userId', String(80), index=False, unique=False, nullable=False),
        Column('tierClassID', Integer, index=False, unique=False, nullable=False, default=1),
        Column('innerTierLevel', Integer, index=False, unique=False, nullable=False, default=1),
        Column('cbsdSerialNumber', String(80), index=False, unique=False, nullable=False, default=''),
        Column('cbsdCategory', String(80), index=False, unique=False, nullable=False, default=''),
        Column('cbsdInfo', String(80), index=False, unique=False, nullable=False, default=''),
        Column('callSign', String(80), index=False, unique=False, nullable=False, default=''),
        Column('airInterface', String(80), index=False, unique=False, nullable=False, default=''),
        Column('installationParam', String(80), index=False, unique=False, nullable=False, default=''),
        Column('measCapability', String(80), index=False, unique=False, nullable=False, default=''),
        Column('groupingParam', String(80), index=False, unique=False, nullable=False, default=''),
        Column('fullyTrusted', String(80), index=False, unique=False, nullable=False, default=''),
        Column('comment', String(80), index=False, unique=False, nullable=False, default=''),
        Column('justChangedParams', Boolean, index=False, unique=False, nullable=False, default=False),
        Column('sid', String(80), index=False, unique=False, nullable=False),
        Column('priorityScore', Integer, default=0)
    )
