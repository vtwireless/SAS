import random
import uuid
import threading
import math
import time
from datetime import datetime, timezone, timedelta
import logging

import sqlalchemy as db
import sqlalchemy.exc
from sqlalchemy import select, and_, insert, delete, update
from sqlalchemy.engine import CursorResult

from settings import settings
from algorithms import SASREM
from algorithms.SASAlgorithms import SASAlgorithms
from Utilities import Utilities
from algorithms import CBSD
from algorithms import Server_WinnForum as WinnForum
from algorithms import PrioritizationFramework


class USRPController:
    USRP = None
    log = logging.getLogger(settings.APP_NAME + ".USRPController")


    def __init__(self, metadata, engine, connection, algorithms):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms = algorithms
        self._set_usrp_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)

        try:
            queryResult = resultProxy.fetchall()
            rows = [row._asdict() for row in queryResult]

            return rows

        except sqlalchemy.exc.ResourceClosedError:
            return None

    def _set_usrp_table(self):
        self.USRP = db.Table(
            settings.USRP_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )


    def get_usrps(self):
        query = select([self.USRP])
        self.log.debug("Getting usrps...")
        try:
            rows = self._execute_query(query)

            return {
                'status': 1,
                'usrps': rows
            }
        except Exception as err:
            raise Exception(str(err))


    def create_usrp(self, payload):

        Node = payload['usrps']['Node']
        Device = payload['usrps']['Device']
        SerialNo = payload['usrps']['SerialNo']
        InventoryNo = payload['usrps']['InventoryNo']
        Operational = payload['usrps']['Operational']
        IP = payload['usrps']['IP']
        TimingSource = payload['usrps']['TimingSource']
        DBoard_A = payload['usrps']['DBoard_A']
        DBoard_B = payload['usrps']['DBoard_B']
        TX_RX_1=payload['usrps']['TX_RX_1']
        RX_1 = payload['usrps']['RX_1']
        TX_RX_2=payload['usrps']['TX_RX_2']
        RX_2 = payload['usrps']['RX_2']
        Xmm = payload['usrps']['Xmm']
        Ymm = payload['usrps']['Ymm']
        Zmm = payload['usrps']['Zmm']
        Daughterboard = payload['usrps']['Daughterboard']
        CurrentLocation = payload['usrps']['CurrentLocation']
        PowerSupplyIssue = payload['usrps']['PowerSupplyIssue']
        Extraction_from_setup = payload['usrps']['Extraction_from_setup']
        Comments = payload['usrps']['Comments']

        query = select([self.USRP])
        insertQuery = insert(self.USRP).values(
            Node = Node, Device = Device, SerialNo = SerialNo, InventoryNo = InventoryNo,
            Operational = Operational, IP = IP, TimingSource = TimingSource,DBoard_A = DBoard_A,
            DBoard_B = DBoard_B,TX_RX_1 = TX_RX_1,RX_1 = RX_1, TX_RX_2 = TX_RX_2,RX_2 = RX_2,Xmm = Xmm,
            Ymm = Ymm, Zmm = Zmm, Daughterboard = Daughterboard, CurrentLocation = CurrentLocation,
            PowerSupplyIssue = PowerSupplyIssue, Extraction_from_setup = Extraction_from_setup,
            Comments = Comments
        )
        self.CONNECTION.execute(insertQuery)

        return {
            "status": 1,
            "message": "usrp has been added."
        }

        rows = self._execute_query(query)

        if len(rows) > 0:
            return None

        self.CONNECTION.execute(self.USRP.insert(), [payload])

        rows = self._execute_query(query)
        if len(rows) < 1:
            return None

        return rows