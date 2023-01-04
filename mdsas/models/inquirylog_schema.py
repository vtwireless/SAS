from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.INQUIRYLOG, metadata,
        Column('inquiryLogID', Integer, primary_key=True, autoincrement=True),
        Column('timestamp', Integer, index=False),
        Column('cbsdId', Integer, index=False, unique=False, nullable=False, default=False),
        Column('requestLowFrequency', Float, index=False, unique=False, nullable=False, default=0),
        Column('requestHighFrequency', Float, index=False, unique=False, nullable=False, default=0),
        Column('responseCode', Integer, index=False, unique=False),
        Column('responseMessage', String, index=False, unique=False),
        Column('availableChannels', Float, index=False, unique=False),
        Column('ruleApplied', String, index=False, unique=False),
        Column('maxEIRP', Float, index=False, unique=False),
    )
