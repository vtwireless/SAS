from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy import Table

from settings import settings


def set_schema(metadata):
    """
    UPDATE regionSchedule SET
        regionName = '$regionName', regionShape = '$regionShape', shapeRadius = '$shapeRadius',
        shapePoints = '$shapePoints', schedulingAlgorithm = '$schedulingAlgorithm', useSUTiers = '$useSUTiers',
        useClassTiers = '$useClassTiers', useInnerClassTiers = '$useInnerClassTiers', isDefault = '$isDefault',
        isActive = '$isActive'
    WHERE regionID = '$regionID' LIMIT 1
    """
    Table(
        settings.REGIONSCHEDULE, metadata,
        Column('regionID', Integer, primary_key=True, autoincrement=True),
        Column('regionName', String(80), index=False, unique=True, nullable=False, default=''),
        Column('regionShape', String(80), index=False, unique=False, nullable=False, default=''),
        Column('shapeRadius', String(80), index=False, unique=False, nullable=False, default=''),
        Column('shapePoints', String(80), index=False, unique=False, nullable=False, default=''),
        Column('schedulingAlgorithm', String(80), index=False, unique=False, nullable=False, default=''),
        Column('useSUTiers', Boolean, index=False, unique=False, nullable=False),
        Column('useClassTiers', Boolean, index=False, unique=False, nullable=False),
        Column('useInnerClassTiers', Boolean, index=False, unique=False, nullable=False),
        Column('isDefault', Boolean, index=False, unique=False, nullable=False),
        Column('isActive', Boolean, index=False, unique=False, nullable=False)
    )
