from sqlalchemy import Column, String, Integer, Float, SmallInteger, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.BASESTATION_TABLE, metadata,
        Column("bsID", Integer, primary_key=True, autoincrement=True),
        Column('location', String(80), index=False, unique=False, nullable=False, default=''),
        Column('IPAddress', String(80), index=False, unique=False, nullable=True),
        Column('minFrequency', Float, index=False, unique=False, nullable=False),
        Column('maxFrequency', Float, index=False, unique=False, nullable=False),
        Column('status', String(80), index=False, unique=False, nullable=False),
    )
