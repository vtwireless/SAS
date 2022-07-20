from .. import database


class Node(database.Model):
    """Data model for user accounts."""

    __tablename__ = 'node'

    fccId = database.Column(database.String(80), index=True, unique=True, nullable=False, primary_key=True)
    nodeName = database.Column(database.String(80), index=False, unique=False, nullable=False)
    location = database.Column(database.String(80), index=False, unique=False, nullable=False, default='')
    trustLevel = database.Column(database.Integer, index=False, unique=False, nullable=False)
    ipAddress = database.Column(database.String(80), index=False, unique=False, nullable=False)
    minFrequency = database.Column(database.Float, index=False, unique=False, nullable=False)
    maxFrequency = database.Column(database.Float, index=False, unique=False, nullable=False)
    minSampleRate = database.Column(database.Float, index=False, unique=False, nullable=False)
    maxSampleRate = database.Column(database.Float, index=False, unique=False, nullable=False)
    nodeType = database.Column(database.String(80), index=False, unique=False, nullable=False)
    mobility = database.Column(database.SmallInteger, index=False, unique=False, nullable=False)
    status = database.Column(database.String(80), index=False, unique=False, nullable=False)
    userId = database.Column(database.String(80), index=False, unique=False, nullable=False)
    cbsdSerialNumber = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    cbsdCategory = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    cbsdInfo = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    callSign = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    airInterface = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    installationParam = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    measCapability = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    groupingParam = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    fullyTrusted = database.Column(database.String(80), index=False, unique=False, nullable=False, defualt='')
    comment = database.Column(database.String(80), index=False, unique=False, nullable=False)
