from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.TIERCLASS, metadata,
        Column('tierClassID', Integer, primary_key=True, autoincrement=True),
        Column('tierClassName', String(80), index=False, unique=True, nullable=False, default=''),
        Column('tierPriorityLevel', Integer, nullable=False, default=1),
        Column('tierClassDescription', String(80), index=False, unique=False, nullable=False, default=''),
        Column('maxTierNumber', String(80), index=False, unique=False, nullable=False, default=''),
        Column('tierUpperBand', String(80), index=False, unique=False, nullable=False, default=''),
        Column('tierLowerBand', String(80), index=False, unique=False, nullable=False, default='')
    )
