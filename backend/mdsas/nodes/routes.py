import threading
import uuid

from flask import request, Blueprint

from .models import database, Node
from ..library.Utility import Utility
from ..library import SASREM
from ..library.SASAlgorithms import SASAlgorithms

node_routes = Blueprint('node_routes', __name__)


@node_routes.route('/nodes', methods=['GET'])
def get_nodes():
    nodes: Node = Node.query.all()
    returnable = {
        c.key: getattr(nodes, c.key) for c in database.inspect(nodes).mapper.column_attrs
    }

    return Utility.success_payload({"nodes": returnable})


@node_routes.route('/createNode', methods=['POST'])
def create_node():
    payload = request.get_json()
    nodeName = payload.get('nodeName', '')
    if not nodeName:
        return Utility.failure_message('Node name not provided')

    SUID = payload.get('SUID', nodeName)
    fccId = payload.get('fccId', SUID)
    measCapability = payload.get('measCapability', '')

    existing_node = Node.query.filter(
        (Node.fccId == fccId) & (Node.nodeName == nodeName)
    ).first()

    if existing_node:
        return Utility.already_exists("A node already exists with the same name")

    mobility = payload.get('mobility', 'False').lower()
    if mobility == 'false':
        mobility = 0
    else:
        mobility = 1

    node: Node = Node(
        fccId=fccId,
        nodeName=nodeName,
        location=payload.get('location', ''),
        trustLevel=int(payload.get('trustLevel', '5')),
        ipAddress=payload.get('IPAddress', ''),
        minFrequency=float(payload.get('minFrequency', '0')),
        maxFrequency=float(payload.get('maxFrequency', '0')),
        minSampleRate=float(payload.get('minSampleRate', '0')),
        maxSampleRate=float(payload.get('maxSampleRate', '0')),
        nodeType=payload.get('nodeType', ''),
        mobility=mobility,
        status=payload.get('status', ''),
        comment=payload.get('comment', ''),
        userId=payload.get('userId', ''),
        cbsdSerialNumber=payload.get('cbsdSerialNumber', ''),
        cbsdCategory=payload.get('cbsdCategory', ''),
        cbsdInfo=payload.get('cbsdInfo', ''),
        callSign=payload.get('callSign', ''),
        airInterface=payload.get('airInterface', ''),
        installationParam=payload.get('installationParam', ''),
        measCapability=measCapability,
        groupingParam=payload.get('groupingParam', ''),
        fullyTrusted=payload.get('groupingParam', '')
    )
    try:
        database.session.add(node)
        database.session.commit()

        if measCapability:
            sid = ''  # TODO: implementation
            radio = SASREM.CBSDSocket(fccId, sid, False)  # TODO: move to models
            send_assignment_to_radio(radio)

        return Utility.success_message("Node has been added.")

    except Exception as e:
        return Utility.failure_message(str(e))


def send_assignment_to_radio(radio):
    # todo: Maintain all radios

    # 3.5 GHz CBRS Band is 150 MHz wide
    freqRange = SASAlgorithms.MAXCBRSFREQ - SASAlgorithms.MINCBRSFREQ
    blocks = freqRange / SASAlgorithms.TENMHZ

    for i in range(int(blocks)):
        low = (i * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        high = ((i + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ
        result = SASAlgorithms.isPUPresentREM(REM, low, high, None, None, None)
        if result == 2:
            # if there is no spectrum data available for that frequency range assign radio to it
            changeParams = dict()
            changeParams["lowFrequency"] = str((SASAlgorithms.TENMHZ * i) + SASAlgorithms.MINCBRSFREQ)
            changeParams["highFrequency"] = str((SASAlgorithms.TENMHZ * (i + 1)) + SASAlgorithms.MINCBRSFREQ)
            changeParams["cbsdId"] = radio.cbsdId
            radio.justChangedParams = True
            socket.emit("changeRadioParams", to=radio.sid, data=changeParams)
            break

    threading.Timer(3.0, resetRadioStatuses, [[radio]]).start()
