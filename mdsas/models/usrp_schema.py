from sqlalchemy import Column, String, Integer, Float, SmallInteger, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    Table(
        settings.USRP_TABLE, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('Node', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Device', String(80), index=False, unique=False, nullable=False, default=''),
        Column('SerialNo', String(80), index=False, unique=False, nullable=False, default=''),
        Column('InventoryNo', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Operational', String(80), index=False, unique=False, nullable=False, default=''),
        Column('IP', String(80), index=False, unique=False, nullable=False, default=''),
        Column('TimingSource', String(80), index=False, unique=False, nullable=False, default=''),
        Column('DBoard_A', String(80), index=False, unique=False, nullable=False, default=''),
        Column('DBoard_B', String(80), index=False, unique=False, nullable=False, default=''),
        Column('TX_RX_1', String(80), index=False, unique=False, nullable=False, default=''),
        Column('RX_1', String(80), index=False, unique=False, nullable=False, default=''),
        Column('TX_RX_2', String(80), index=False, unique=False, nullable=False, default=''),
        Column('RX_2', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Xmm', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Ymm', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Zmm', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Daughterboard', String(80), index=False, unique=False, nullable=False, default=''),
        Column('CurrentLocation', String(80), index=False, unique=False, nullable=False, default=''),
        Column('PowerSupplyIssue', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Extraction_from_setup', String(80), index=False, unique=False, nullable=False, default=''),
        Column('Comments', String(80), index=False, unique=False, nullable=False, default=''),

    )