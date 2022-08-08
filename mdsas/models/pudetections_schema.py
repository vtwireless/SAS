from sqlalchemy import Column, String, Integer, Float
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.PUDETECTIONS, metadata,
        Column('timestamp', String(80), nullable=False),
        Column('reportId', String(80), index=True, unique=True, nullable=False, primary_key=True),
        Column('lowFreq', Float, nullable=False),
        Column('highFreq', Float, nullable=False),
        Column('result', Integer, nullable=False)
    )
