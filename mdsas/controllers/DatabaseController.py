import os
import sys
import os
import uuid
import threading
import time
import sqlalchemy as db
from sqlalchemy import select, insert, delete, update, and_
from sqlalchemy.engine import CursorResult
from datetime import datetime, timedelta, timezone

from Utilities import Utilities
from algorithms import CBSD
from algorithms import SASREM
from settings import settings
from models.Schemas import Schemas
from controllers.CBSDController import CBSDController
from controllers.GrantController import GrantController
from controllers.SettingsController import SettingsController
from controllers.TierClassController import TierClassController
from controllers.UsersController import UsersController
from algorithms.SASAlgorithms import SASAlgorithms
from algorithms import Server_WinnForum as WinnForum


class DatabaseController:
    ENGINE = None
    CONNECTION = None
    METADATA = None

    algorithms: SASAlgorithms = SASAlgorithms()
    rem = SASREM.SASREM()

    USERS = None
    NODES = None
    GRANTS = None
    PUDETECTIONS = None
    REGIONSCHEDULE = None
    GRANTLOG = None

    __grantRecords = []
    __allRadios = []

    def __init__(self, LOAD_SEED_DATA):
        self._delete_db_file()

        if settings.ENVIRONMENT == 'DEVELOPMENT':
            self._connect_to_dev_db()
        else:
            self._connect_to_prod_db()

        # Initialize tables
        self.schemas = Schemas(self.METADATA)
        self._set_tables()
        self._get_tables()

        if LOAD_SEED_DATA:
            self.load_seed_data()

    # In[ --- Private Helper Functions --- ]
    def load_seed_data(self):
        # self.users_controller.load_seed_data()
        # self.tierclass_controller.load_seed_data()
        # self.cbsd_controller.load_seed_data()
        pass

    def _connect_to_dev_db(self):
        self.ENGINE = db.create_engine(settings.DEVELOPMENT_DATABASE_URI)
        self.CONNECTION = self.ENGINE.connect()
        self.METADATA = db.MetaData()

    def _connect_to_prod_db(self):
        self.ENGINE = db.create_engine(settings.PRODUCTION_DATABASE_URI)
        self.CONNECTION = self.ENGINE.connect()
        self.METADATA = db.MetaData()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def _delete_table(self, table: db.Table):
        table.drop(self.ENGINE)

    def _delete_all_tables(self):
        self.METADATA.drop_all(self.ENGINE)

    @staticmethod
    def _delete_db_file():
        try:
            os.remove(settings.SQLITE_FILE)
        except Exception as exception:
            print(str(exception))

    def _disconnect_from_db(self):
        self.CONNECTION.close()
        self._delete_db_file()

    # In[ --- CREATE TABLES --- ]

    def _set_tables(self):
        self.schemas.create_tables()
        self.METADATA.create_all(self.ENGINE)

    def _get_tables(self):
        # TODO: Migrate Controllers
        self.settings_controller = SettingsController(self.METADATA, self.ENGINE, self.CONNECTION, self.algorithms)
        self.users_controller = UsersController(self.METADATA, self.ENGINE, self.CONNECTION, self.algorithms)
        self.tierclass_controller = TierClassController(self.METADATA, self.ENGINE, self.CONNECTION, self.algorithms)
        self.cbsd_controller = CBSDController(self.METADATA, self.ENGINE, self.CONNECTION, self.algorithms)
        self.grants_controller = GrantController(
            self.METADATA, self.ENGINE, self.CONNECTION, self.algorithms, self.cbsd_controller
        )

        # self._get_secondaryUser_table()
        # self._get_nodes_table()
        # self._get_grants_table()
        self._get_pudetections_table()
        # self._get_tierclass_table()
        # self._get_tierassignment_table()

    # In[ --- SETTINGS CONTROLS --- ]

    def get_sas_settings(self, algorithm=None):
        self.settings_controller.get_sas_settings(algorithm)

    def set_algorithm_settings(self, result):
        self.settings_controller.set_algorithm_settings(result)

    def create_sas_settings(self, data=None):
        self.settings_controller.create_sas_settings(data)

    def update_sas_settings(self, data):
        self.settings_controller.update_sas_settings(data)

    # In[ --- USER CONTROLS --- ]

    def get_secondary_users(self):
        return self.users_controller.get_secondary_users()

    def get_secondary_user(self, payload):
        return self.users_controller.get_secondary_user(payload)

    def authenticate_user(self, payload: any, isAdmin: bool):
        return self.users_controller.authenticate_user(payload, isAdmin)

    def create_user(self, payload, isAdmin):
        return self.users_controller.create_user(payload, isAdmin)

    def check_email_availability(self, payload):
        return self.users_controller.check_email_availability(payload)

    # In[ --- TIER CONTROLS --- ]

    def get_tierclass_by_id(self, payload):
        return self.tierclass_controller.get_tierclass_by_id(payload)

    def get_tierclass(self):
        return self.tierclass_controller.get_tierclass()

    def create_tierclass(self, payload):
        return self.tierclass_controller.create_tierclass(payload)

    # def update_tierclass(self, payload):
    #     try:
    #         return self.tierclass_controller.update_tierclass(payload)
    #     except Exception as err:
    #         raise Exception(str(err))
    #
    # def alter_tierclass_assignment(self, payload):
    #     try:
    #         return self.tierclass_controller.alter_tierclass_assignment(payload)
    #     except Exception as err:
    #         raise Exception(str(err))
    #
    # def delete_tierclass_assignment(self, payload):
    #     try:
    #         return self.tierclass_controller.delete_tierclass_assignment(payload)
    #     except Exception as err:
    #         raise Exception(str(err))

    # In[ --- REGION SCHEDULE CONTROLS --- ]

    def _get_region_schedule_table(self):
        self.REGIONSCHEDULE = db.Table(
            settings.REGIONSCHEDULE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    def create_region_schedule(self, payload):
        regionName = payload['regionName']
        regionShape = payload['regionShape']
        shapeRadius = payload['shapeRadius']
        shapePoints = payload['shapePoints']
        schedulingAlgorithm = payload['schedulingAlgorithm']
        useSUTiers = payload['useSUTiers']
        useClassTiers = payload['useClassTiers']
        useInnerClassTiers = payload['useInnerClassTiers']
        isDefault = payload['isDefault']
        isActive = payload['isActive']

        # $regionName == "" ||
        # ($regionShape != "circle" && $regionShape != "polygon") ||
        # $schedulingAlgorithm == "" || $useSUTiers == "" || $useClassTiers == ""
        # || $useInnerClassTiers == "" || $isDefault == "" || $isActive == ""
        if not regionName or (regionShape != "circle" and regionShape != "polygon") or not schedulingAlgorithm \
                or not useSUTiers or not useClassTiers or not useInnerClassTiers or not isDefault or not isActive \
                or (regionShape == "circle" and shapeRadius == ""):
            return {
                'status': 0,
                'message': 'All parameters not provided'
            }

        query = select([self.REGIONSCHEDULE]).where(
            self.REGIONSCHEDULE.columns.regionName == regionName
        )
        rows = self._execute_query(query)
        if len(rows) > 1:
            return {
                'status': 0,
                'message': 'Region Schedule created successfully'
            }

        self.CONNECTION.execute(self.REGIONSCHEDULE.insert(), [payload])

    def update_region_schedule(self, payload):
        regionID = payload['regionID']
        regionName = payload['regionName']
        regionShape = payload['regionShape']
        shapeRadius = payload['shapeRadius']
        shapePoints = payload['shapePoints']
        schedulingAlgorithm = payload['schedulingAlgorithm']
        useSUTiers = payload['useSUTiers']
        useClassTiers = payload['useClassTiers']
        useInnerClassTiers = payload['useInnerClassTiers']
        isDefault = payload['isDefault']
        isActive = payload['isActive']

        # $regionName == "" ||
        # ($regionShape != "circle" && $regionShape != "polygon") ||
        # $schedulingAlgorithm == "" || $useSUTiers == "" || $useClassTiers == ""
        # || $useInnerClassTiers == "" || $isDefault == "" || $isActive == ""
        if not regionName or (regionShape != "circle" and regionShape != "polygon") or not schedulingAlgorithm \
                or not useSUTiers or not useClassTiers or not useInnerClassTiers or not isDefault or not isActive \
                or (regionShape == "circle" and shapeRadius == ""):
            return {
                'status': 0,
                'message': 'All parameters not provided'
            }

        updateQuery = update(self.REGIONSCHEDULE) \
            .where(self.REGIONSCHEDULE.columns.regionID == regionID) \
            .values(
            regionName=regionName, regionShape=regionShape,
            shapeRadius=shapeRadius, schedulingAlgorithm=schedulingAlgorithm,
            useSUTiers=useSUTiers, useClassTiers=useClassTiers,
            shapePoints=shapePoints, useInnerClassTiers=useInnerClassTiers, isDefault=isDefault,
            isActive=isActive
        )
        ResultProxy = self.CONNECTION.execute(updateQuery)

        return {
            'status': 1,
            'message': 'Region Schedule updated successfully'
        }

    # In[ --- NODE CONTROLS --- ]

    # def _get_nodes_table(self):
    #     self.NODES = db.Table(
    #         settings.NODE_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
    #     )

    def get_nodes(self):
        return self.cbsd_controller.get_cbsd()

    def _get_node_by_cbsdId(self, cbsdId):
        return self.cbsd_controller.get_cbsd_by_id(cbsdId)

    def register_nodes(self, sid, payload):
        return self.cbsd_controller.register_cbsds(sid, payload)

    def deregister_nodes(self, nodes):
        for item in nodes["deregistrationRequest"]:
            if 'cbsdId' not in item or not item['cbsdId']:
                raise Exception(str('CBSD-ID not provided'))

            self.grants_controller.cancel_grants_for_cbsd(item['cbsdId'])

        return self.cbsd_controller.deregister_cbsds(nodes)

    def update_nodes(self, payload):
        self.cbsd_controller.update_cbsd(payload)

    # In[ --- BaseStation CONTROLS --- ]

    def get_base_station(self):
        return self.cbsd_controller.get_bstation()

    def get_base_station_by_id(self, bsID):
        return self.cbsd_controller.get_bstation_by_id(bsID)

    def register_base_stations(self, payload):
        returnable = []
        for entry in payload:
            returnable.append(self.cbsd_controller.create_bstation(entry))

        if len(payload) != len(returnable):
            status = 0
        else:
            status = 1

        return {
            "status": status,
            "base_stations": returnable
        }

    def change_base_station_status(self, payload):
        return self.cbsd_controller.change_bstation_status(payload)

    # In[ --- GRANT CONTROLS --- ]

    # def get_grant_records(self):
    #     return self.__grantRecords

    def get_grants(self):
        return self.grants_controller.get_grants()

    def get_inquiries(self):
        return self.grants_controller.get_inquiries()

    def get_grant_with_id(self, grantId):
        return self.grants_controller.get_grant_with_id(grantId)

    # def _get_grants_table(self):
    #     self.GRANTS = db.Table(
    #         settings.GRANT_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
    #     )

    def spectrum_inquiry(self, data):
        return self.grants_controller.spectrum_inquiry(data)

    def create_grant_request(self, payload):
        return self.grants_controller.grant_request(payload)

    def heartbeat_request(self, data):
        return self.grants_controller.heartbeat_request(data)

    def cancel_grant(self, grant):
        self.grants_controller.cancel_grant_by_grantId(grant)

    def delete_grant_by_id(self, payload):
        self.grants_controller.delete_grant_with_id(payload['grantId'])

    def relinquishment_request(self, data):
        return self.grants_controller.relinquishment_request(data)

    def spectrumData(self, jsonData):
        return self.grants_controller.spectrumData(jsonData)

    # def _get_grantlog_table(self):
    #     self.GRANTLOG = db.Table(
    #         settings.GRANTLOG, self.METADATA, autoload=True, autoload_with=self.ENGINE
    #     )
    #
    # def log_grant(self, payload):
    #     if not payload['grantID'] or not payload['status']:
    #         return {
    #             'status': 0,
    #             'message': 'All parameters were not provided'
    #         }
    #
    #     query = select([self.GRANTLOG]).where(and_(
    #         self.GRANTLOG.columns.grantLogID == payload['grantLogID'],
    #         self.GRANTLOG.columns.secondaryUserID == payload['secondaryUserID']
    #     ))
    #     rows = self._execute_query(query)
    #
    #     if len(rows) > 0:
    #         message = f"Grant already logged."
    #         return {
    #             "status": 0,
    #             "exists": 1,
    #             "message": message
    #         }
    #
    #     self.CONNECTION.execute(self.GRANTLOG.insert(), [payload])
    #
    #     rows = self._execute_query(query)
    #     if len(rows) < 1:
    #         message = f"Grant could not be logged"
    #         return {
    #             "status": 0,
    #             "message": message
    #         }
    #
    #     return {
    #         "status": 1,
    #         "message": f"Grant {payload['grantLogID']} logged."
    #     }

    # In[ --- PU DETECTIONS CONTROLS --- ]

    def _get_pudetections_table(self):
        self.PUDETECTIONS = db.Table(
            settings.PUDETECTIONS, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    def get_pudetections(self):
        query = select([self.PUDETECTIONS])

        try:
            rows = self._execute_query(query)

            return {
                'status': 1,
                'puDetections': rows
            }
        except Exception as err:
            raise Exception(str(err))

    def get_pudetection_by_id(self, reportId):
        query = select([self.PUDETECTIONS]).where(
            self.PUDETECTIONS.columns.reportId == reportId
        )

        try:
            rows = self._execute_query(query)

            return {
                'status': 1,
                'puDetection': rows
            }
        except Exception as err:
            raise Exception(str(err))

    def set_pudetections(self, insertionArr):
        try:
            self.CONNECTION.execute(self.PUDETECTIONS.insert(), insertionArr)
        except Exception as err:
            print(str(err))
            return {
                "status": 0,
                "message": f"PU Detections could not be added due to '{str(err)}'."
            }

        return {
            "status": 1,
            "message": "PU Detections recorded"
        }

    def check_pudetections(self, data=None):
        report, pauseArr, insertionArr = [], [], []
        freqRange = self.algorithms.MAXCBRSFREQ - self.algorithms.MINCBRSFREQ
        blocks = freqRange / self.algorithms.TENMHZ
        grants = self.get_grants()['spectrumGrants']

        for i in range(int(blocks)):
            low = (i * self.algorithms.TENMHZ) + self.algorithms.MINCBRSFREQ
            high = ((i + 1) * self.algorithms.TENMHZ) + self.algorithms.MINCBRSFREQ
            result = self.algorithms.isPUPresentREM(
                self.rem, low, high, None, None, None
            )

            if result == 1:
                if data:
                    insertionArr.append({
                        "reportId": data["reportId"],
                        "timestamp": str(int(time.time())),
                        "lowFreq": low,
                        "highFreq": high,
                        "result": int(result)
                    })

                    for grant in grants:
                        isOverlap = self.algorithms.frequencyOverlap(
                            low, high, grant.minFrequency, grant.maxFrequency
                        )
                        # TODO: CBSD and NODE are not in sync. Currently, cbsd doesn't have an sid
                        node = self._get_node_by_cbsdId(grant.cbsdId)

                        if isOverlap and node:
                            pauseArr.append({
                                'grantId': grant.grantId,
                                'sid': node.sid
                            })
                    report.append("PU FOUND")
            elif result == 0:
                report.append("PU NOT FOUND")
            elif result == 2:
                report.append("NO SPECTRUM DATA")

        self.set_pudetections(insertionArr)

        return report, pauseArr

    # In[ --- OTHERS --- ]

    def incumbentInformation(self, incumbentData):
        """Function for PUs to send their operating data"""
        utilizeExtraChannel, obfuscated = True, []  # TODO: Decide when to toggle this

        for data in incumbentData["incumbentInformation"]:
            lowFreq, highFreq = None, None
            # Get time, location, and frequency range of PU
            desireObfuscation, scheme, startTime, endTime = [None] * 4
            puLat, puLon, puLowFreq, puLighFreq, power = [None] * 5

            try:
                desireObfuscation = bool(data["desireObfuscation"])
                scheme = str(data["scheme"])
                puLowFreq = float(data["lowFreq"])
                puHighFreq = float(data["highFreq"])
                puLat = data["puLat"]
                puLon = data["puLon"]
                power = data["power"]
                startTime = data["startTime"]
                endTime = data["endTime"]
            except Exception as err:
                raise Exception(str(err))

            if desireObfuscation:
                if scheme:
                    # TODO: Remove allRadios
                    est_num_of_available_sus = 0
                    for radio in self.__allRadios:
                        if not radio.justChangedParams:
                            est_num_of_available_sus += 1

                    if scheme == "double_pad":
                        lowFreq, highFreq = Utilities.double_pad_obfuscate(
                            puLowFreq, puHighFreq, est_num_of_available_sus
                        )
                    elif scheme == "fill_channel":
                        lowFreq, highFreq = Utilities.fill_channel_obfuscate(
                            puLowFreq, puHighFreq, est_num_of_available_sus
                        )

                    obfuscated.extend(self.sendIICCommand(lowFreq, highFreq))
                else:
                    print("No PU Obfuscation Scheme Detected...")
            else:
                pass  # PU does not want special treatment

        return obfuscated

    def sendIICCommand(self, lowFreq, highFreq):
        """Will ask 1 idle node to transmit over the low-high freq"""

        radiosToChangeBack, obstructionArr = [], []
        # TODO: Remove radios
        for radio in self.__allRadios:
            if not radio.justChangedParams:
                # print("SENDING LOW: " +str(lowFreq)+" and HIGH: "+str(highFreq))
                radio.justChangedParams = True
                obstructionArr.append((radio, lowFreq, highFreq))
                radiosToChangeBack.append(radio)

        threading.Timer(
            5.0, Utilities.resetRadioStatuses, [radiosToChangeBack]
        ).start()

        return obstructionArr
