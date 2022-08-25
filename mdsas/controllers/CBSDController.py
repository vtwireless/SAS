import random
import uuid

import sqlalchemy as db
from sqlalchemy import select, and_, insert, delete, update
from sqlalchemy.engine import CursorResult

from settings import settings
from algorithms import SASREM
from algorithms.SASAlgorithms import SASAlgorithms
from Utilities import Utilities
from algorithms import CBSD
from algorithms import Server_WinnForum as WinnForum


class CBSDController:
    CBSD = None

    def __init__(self, metadata, engine, connection, algorithms):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms = algorithms

        self._set_cbsds_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def _set_cbsds_table(self):
        self.CBSD = db.Table(
            settings.CBSD_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    def get_cbsd(self):
        query = select([self.CBSD])
        rows = self._execute_query(query)

        return {
            'status': 1,
            'nodes': rows
        }

    def get_cbsd_by_id(self, cbsdID):
        query = select([self.CBSD]).where(
            self.CBSD.columns.cbsdID == cbsdID
        )

        rows = self._execute_query(query)

        if len(rows) > 0:
            return Utilities.loadCBSDFromJSON(rows[0])

        return None

    def create_cbsd(self, payload):
        query = select([self.CBSD]).where(and_(
            self.CBSD.columns.fccId == payload['fccId'],
            self.CBSD.columns.IPAddress == payload['IPAddress'],
            self.CBSD.columns.nodeType == payload['nodeType']
        ))
        rows = self._execute_query(query)
        if len(rows) > 0:
            return None

        self.CONNECTION.execute(self.CBSD.insert(), [payload])

        rows = self._execute_query(query)
        if len(rows) < 1:
            return None

        return rows[0]['cbsdID']

    def register_cbsds(self, sid, payload):
        responseArr, assignmentArr = [], []

        for item in payload["registrationRequest"]:
            if not item['fccId']:
                item['fccId'] = str(uuid.uuid4())
            item['sid'] = sid

            cbsdID = self.create_cbsd(item)
            if not cbsdID:
                return {
                    "status": 1,
                    "message": f"Node '{payload['fccID']}' could not be added."
                }

            radio = CBSD.CBSD(cbsdID, item[''], item['fccId'])
            # Flatten Structure
            location = item['location'].split(',')
            radio.latitude = location[0]
            radio.longitude = location[1]
            radio.nodeType = item["nodeType"]
            radio.minFrequency = item["minFrequency"]
            radio.maxFrequency = item["maxFrequency"]
            radio.minSampleRate = item["minSampleRate"]
            radio.maxSampleRate = item["maxSampleRate"]
            radio.mobility = item["mobility"]

            response = WinnForum.RegistrationResponse(radio.id, None, self.algorithms.generateResponse(0))

            if "measCapability" in item:
                cbsd = SASREM.CBSDSocket(radio.id, sid, False)
                assignmentArr.append(cbsd)
                response.measReportConfig = item["measCapability"]

            responseArr.append(response.asdict())

        return {
                   "status": 1,
                   "message": "Nodes have been added.",
                   "registrationResponse": responseArr
               }, assignmentArr

    def deregister_cbsds(self, nodes):
        responseArr = []
        for item in nodes["deregistrationRequest"]:
            if 'cbsdId' not in item or not item['cbsdId']:
                raise Exception(str('CBSD-ID not provided'))

            query = delete([self.CBSD]).where(
                self.CBSD.columns.cbsdId == item['cbsdId']
            )
            rows = self._execute_query(query)

            response = WinnForum.DeregistrationResponse()
            response.cbsdId = item['cbsdId']

            query = select([self.CBSD]).where(and_(
                self.CBSD.columns.cbsdId == item['cbsdId']
            ))
            rows = self._execute_query(query)

            if len(rows) > 0:
                response.response = self.algorithms.generateResponse(0)
            else:
                response.response = self.algorithms.generateResponse(103)

            responseArr.append(response.asdict())

        return {
            'status': 0,
            'message': 'Node Deregistration complete',
            'deregistrationResponse': responseArr
        }

    def update_cbsd(self, payload):
        if 'cbsdId' not in payload or not payload['cbsdId']:
            raise Exception(str('CBSD-ID not provided'))

        radioObj: CBSD.CBSD = Utilities.loadCBSDFromJSON(payload)

        updateQuery = update(self.CBSD) \
            .where(self.CBSD.columns.cbsdID == payload['cbsdID']) \
            .values(
            trustLevel=radioObj.trustLevel, IPAddress=radioObj.IPAddress,
            minFrequency=radioObj.minFrequency, maxFrequency=radioObj.maxFrequency,
            minSampleRate=radioObj.minSampleRate, maxSampleRate=radioObj.maxSampleRate,
            nodeType=radioObj.nodeType, mobility=radioObj.mobility, status=radioObj.status,
            comment=radioObj.comment, fccId=radioObj.fccId, cbsdSerialNumber=radioObj.cbsdSerialNumber,
            callSign=radioObj.callSign, cbsdCategory=radioObj.cbsdCategory, cbsdInfo=radioObj.cbsdInfo,
            airInterface=radioObj.airInterface, installationParam=radioObj.installationParam,
            measCapability=radioObj.measCapability, groupingParam=radioObj.groupingParam
        )
        ResultProxy = self.CONNECTION.execute(updateQuery)

    def update_cbsd_justChangedParams(self, cbsdId, param):
        updateQuery = update(self.CBSD) \
            .where(self.CBSD.columns.cbsdID == cbsdId) \
            .values(justChangedParams=param)
        ResultProxy = self.CONNECTION.execute(updateQuery)

    def load_seed_data(self):
        self.create_cbsd(self.generate_seed_payload(
            'node1', '30.2234,-80.7756', '1.1.1.1', 1200000000, 1300000000, 1000, 2000, 'VT-CRTS-Node', 0, 'ACTIVE',
            'abc@abc.com', 1, 1
        ))
        self.create_cbsd(self.generate_seed_payload(
            'node2', '30.3234,-80.7756', '1.1.1.1', 1200000000, 1300000000, 1000, 2000, 'VT-CRTS-Node', 0, 'ACTIVE',
            'bbc@abc.com', 1, 1
        ))
        self.create_cbsd(self.generate_seed_payload(
            'node3', '30.4234,-80.7756', '1.1.1.1', 1200000000, 1300000000, 1000, 2000, 'VT-CRTS-Node', 0, 'ACTIVE',
            'cbc@abc.com', 1, 1
        ))

    @staticmethod
    def generate_seed_payload(name, location, ip, minf, maxf, minsr, maxsr, type, mobility, status, userid, tierclass,
                              itl):
        return {
            'fccId': str(uuid.uuid4()),
            'name': name,
            'location': location,
            'trustLevel': random.randint(0, 10),
            'IPAddress': ip,
            'minFrequency': minf,
            'maxFrequency': maxf,
            'minSampleRate': minsr,
            'maxSampleRate': maxsr,
            'nodeType': type,
            'mobility': mobility,
            'status': status,
            'userId': userid,
            'tierClassID': tierclass,
            'innerTierLevel': itl,
            'cbsdSerialNumber': 'AAAA',
            'cbsdCategory': 'CAT1',
            'cbsdInfo': 'INFORMATION',
            'callSign': 'MAVERICK',
            'airInterface': '',
            'installationParam': '',
            'measCapability': '',
            'groupingParam': '',
            'fullyTrusted': '',
            'comment': '',
            'sid': 100
        }
