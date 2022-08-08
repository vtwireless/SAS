from sqlalchemy import Column, String, Integer
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.SETTINGS_TABLE, metadata,
        Column('algorithm', String(80), primary_key=True, nullable=False),
        Column('heartbeatInterval', Integer, nullable=False),
        Column('REMAlgorithm', String(80), nullable=False)
    )
