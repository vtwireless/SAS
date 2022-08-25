from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.TIERASSIGNMENT, metadata,
        Column('tierAssignmentID', Integer, primary_key=True, autoincrement=True),
        Column('tierClassID', String(80), index=False, unique=False, nullable=False),
        Column('secondaryUserID', String(80), index=False, unique=True, nullable=False),
        Column('innerTierLevel', Integer, index=False, unique=False, nullable=False)
    )
