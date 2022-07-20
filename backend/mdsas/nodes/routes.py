from flask import request, Blueprint

from .models import database, Node
from ..library.Utility import Utility

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
            # TODO: Send assignments to Radio
            pass

        return Utility.success_message("Node has been added.")

    except Exception as e:
        return Utility.failure_message(str(e))


def send_assignment_to_radio(radio):
    pass
