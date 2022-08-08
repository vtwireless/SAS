from sqlalchemy import Column, String, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.SECONDARY_USER_TABLE, metadata,
        Column('username', String(80), nullable=False),
        Column('email', String(80), index=True, unique=True, nullable=False, primary_key=True),
        Column('admin', Boolean, nullable=False),
        Column('password', String(80), nullable=False),
        Column('deviceID', String(80), nullable=False),
        Column('location', String(80), nullable=False)
    )
