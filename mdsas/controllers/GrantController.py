import threading
import math
import time
from datetime import datetime, timezone, timedelta
import logging

import pytz
import sqlalchemy as db
import sqlalchemy.exc
from sqlalchemy import select, and_, insert, delete, update
from sqlalchemy.engine import CursorResult

from settings import settings
from Utilities import Utilities
from algorithms import SASREM
from algorithms import Server_WinnForum as WinnForum
from algorithms.SASAlgorithms import SASAlgorithms
from controllers.CBSDController import CBSDController


class GrantController:
    GRANTS = None
    INQUIRIES = None
    log = logging.getLogger(settings.APP_NAME + ".GrantController")

    def __init__(self, metadata, engine, connection, algorithms: SASAlgorithms, nodeCtrl):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms: SASAlgorithms = algorithms
        self.nodeCtrl: CBSDController = nodeCtrl
        self.rem = SASREM.SASREM()

        self._set_grants_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)

        try:
            queryResult = resultProxy.fetchall()
            rows = [row._asdict() for row in queryResult]

            return rows

        except sqlalchemy.exc.ResourceClosedError:
            return None

    def _set_grants_table(self):
        self.GRANTS = db.Table(
            settings.GRANT_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )
        self.INQUIRIES = db.Table(
            settings.INQUIRYLOG, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    def get_grants(self):
        query = select([self.GRANTS])
        self.log.debug("Getting grants...")
        try:
            rows = self._execute_query(query)

            return {
                'status': 1,
                'spectrumGrants': rows
            }
        except Exception as err:
            raise Exception(str(err))

    def get_inquiries(self):
        query = select([self.INQUIRIES])
        self.log.debug("Getting All Spectrum Inquiries")

        rows = self._execute_query(query)

        return {
            'status': 1,
            'spectrumInquiries': rows
        }

    def get_grants_by_freq_range(self, lowFrequency, highFrequency):
        query = select([self.GRANTS]).where(and_(
            self.GRANTS.columns.minFrequency == lowFrequency,
            self.GRANTS.columns.maxFrequency == highFrequency,
        ))
        rows = self._execute_query(query)

        if len(rows) == 0:
            raise Exception(f"Grant could not be found for specified range")
        else:
            return Utilities.loadGrantFromJSON(rows[0])

    def get_grant_with_id(self, grantId):
        query = select([self.GRANTS]).where(
            self.GRANTS.columns.grantId == grantId
        )
        rows = self._execute_query(query)

        if len(rows) == 0:
            raise Exception(f"Grant with Id {grantId} not found")
        else:
            return Utilities.loadGrantFromJSON(rows[0])

    def get_grant_requests_for_cbsd(self, cbsd_id):
        pass

    def delete_grant_with_id(self, grantId):
        query = delete([self.GRANTS]).where(self.GRANTS.columns.grantId == grantId)
        rows = self._execute_query(query)

        query = select([self.GRANTS]).where(self.GRANTS.columns.grantId == grantId)
        rows = self._execute_query(query)
        if len(rows) > 0:
            return {
                "status": 0,
                "message": 'Grant could not be deleted'
            }

        return {
            "status": 1,
            "message": f"Grant {grantId} has been deleted."
        }

    def spectrum_inquiry(self, data):
        inquiryArr, responseArr = [], []
        radiosToChangeBack = []
        radiosToCommunicate = []
        channel_stack = []

        for request in data["spectrumInquiryRequest"]:
            for fr in request["inquiredSpectrum"]:
                minFreq = round(int(fr['lowFrequency']) / self.algorithms.minimumGrantSize) * \
                          self.algorithms.minimumGrantSize
                number_of_channels = math.ceil(
                    (fr['highFrequency'] - fr['lowFrequency']) / self.algorithms.defaultChannelSize
                )

                if minFreq in channel_stack:
                    pass
                else:
                    channel_stack.append(minFreq)

                available_channels, errorCode, response = [], None, None
                for index in range(number_of_channels):
                    lowFreq = minFreq + (index * self.algorithms.defaultChannelSize)
                    highFreq = lowFreq + self.algorithms.defaultChannelSize
                    channelType, ruleApplied = "PAL", "FCC_PART_96"
                    maxEirp = self.algorithms.getMaxEIRP()
                    grantRequests = []  # TODO: Fetch grant requests related to this for this cbsd?

                    if self.algorithms.acceptableRange(lowFreq, highFreq):
                        if 3700000000 > highFreq > 3650000000:
                            channelType = "GAA"

                        present = self.algorithms.isPUPresentREM(
                            self.rem, highFreq, lowFreq, None, None, None
                        )
                        if present == 0:  # No PU is present
                            fr = WinnForum.FrequencyRange(lowFreq, highFreq)
                            availChan = WinnForum.AvailableChannel(fr, channelType, ruleApplied, maxEirp, grantRequests)
                            available_channels.append(availChan)

                        elif present == 2:  # Spectrum Data not available
                            print("~~~~ Something weird happened. I can't explain it ~~~~")
                            rTCB, rTC = self.initiateSensing(lowFreq, highFreq)
                            radiosToChangeBack.extend(rTCB)
                            radiosToCommunicate.extend(rTC)

                        # TODO: present == 1  # PU is present?
                    else:
                        errorCode = 300
                        available_channels = []
                        break

                    if not errorCode:
                        errorCode = 0

                response = WinnForum.SpectrumInquiryResponse(
                    request["cbsdId"], available_channels, self.algorithms.generateResponse(errorCode)
                ).asdict()

                inquiry_log = {
                    "timestamp": int(time.time()),
                    "cbsdId": request["cbsdId"],
                    "responseCode": response["response"]["responseCode"],
                    "responseMessage": response["response"]["responseMessage"]
                }

                if "availableChannel" in response:
                    for channel in response["availableChannel"]:
                        inquiry_log.update({
                            "requestLowFrequency": channel["frequencyRange"]["lowFrequency"],
                            "requestHighFrequency": channel["frequencyRange"]["highFrequency"],
                            "availableChannels": len(available_channels),
                            "ruleApplied": channel["ruleApplied"],
                            "maxEIRP": channel["maxEirp"]
                        })
                else:
                    inquiry_log.update({
                        "requestLowFrequency": fr['lowFrequency'],
                        "requestHighFrequency": fr['highFrequency']
                    })

                inquiryArr.append(response)
                self.CONNECTION.execute(self.INQUIRIES.insert(), [inquiry_log])

        if radiosToChangeBack:
            threading.Timer(
                3.0, self.resetRadioStatuses, [radiosToChangeBack]
            ).start()

        return {
                   'status': 1,
                   "spectrumInquiryResponse": inquiryArr
               }, radiosToCommunicate

    def initiateSensing(self, lowFreq, highFreq):
        count, radioCountLimit = 0, 3
        radiosToChangeBack, radiosToCommunicate = [], []

        allRadios = self.nodeCtrl.get_cbsd()
        for radio in allRadios['nodes']:
            if not radio['justChangedParams']:
                changeParams = dict(
                    lowFrequency=lowFreq,
                    highFrequency=highFreq,
                    cbsdId=radio['cbsdID']
                )
                radio['justChangedParams'] = True
                radiosToChangeBack.append(radio)
                radiosToCommunicate.append({'data': changeParams, 'room': radio['sid']})
                count += 1

            if count >= radioCountLimit or count > len(allRadios) / 3:
                # don't use more than 1/3 of the radios to check band
                break

        return radiosToChangeBack, radiosToCommunicate

    def resetRadioStatuses(self, radios):
        for radio in radios:
            self.nodeCtrl.update_cbsd_justChangedParams(radio['cbsdID'], False)

    def grant_request(self, payload):
        responseArr = []

        for item in payload['grantRequest']:
            if 'secondaryUserID' not in item:
                cbsd = self.nodeCtrl.get_cbsd_by_id(item['cbsdId'])
                item['secondaryUserID'] = cbsd.userId

            minFreq = round(int(item['minFrequency']) / self.algorithms.minimumGrantSize) * \
                      self.algorithms.minimumGrantSize
            number_of_channels = math.ceil(
                (item['maxFrequency'] - item['minFrequency']) / self.algorithms.defaultChannelSize
            )

            for index in range(number_of_channels):
                item["minFrequency"] = minFreq + (index * self.algorithms.defaultChannelSize)
                item["maxFrequency"] = item["minFrequency"] + self.algorithms.defaultChannelSize

                grantRequest = WinnForum.GrantRequest(item["cbsdId"], None)
                ofr = WinnForum.FrequencyRange(item["minFrequency"], item["maxFrequency"])

                grantRequest.operationParam = WinnForum.OperationParam(item["powerLevel"], ofr)
                vtgp = WinnForum.VTGrantParams(
                    item["minFrequency"], item["maxFrequency"], item["preferredFrequency"], item["frequencyAbsolute"],
                    item["minBandwidth"], item["maxBandwidth"], item["preferredBandwidth"],
                    item["startTime"], item["endTime"], item["approximateByteSize"],
                    item["dataType"], item["powerLevel"], item["location"], item["mobility"],
                    item["maxVelocity"]
                )
                grantRequest.vtGrantParams = vtgp

                grants = self.get_grants()['spectrumGrants']
                grantResponse = self.algorithms.runGrantAlgorithm(grants, self.rem, grantRequest)

                if grantResponse.response.responseCode == "0":
                    item["grantExpireTime"] = str(grantResponse.grantExpireTime)
                    item["startepoch"] = int(time.mktime(time.strptime(item["startTime"], "%Y-%m-%dT%H:%M")))
                    item["grantInterval"] = int(time.mktime(time.strptime(item["grantExpireTime"], "%Y-%m-%dT%H:%M"))) \
                        - item["startepoch"]

                item["timestamp"] = int(time.time())
                item["status"] = WinnForum.responseDecode(int(grantResponse.response.responseCode))

                self.CONNECTION.execute(self.GRANTS.insert(), [item])

                # query = select([self.GRANTS]).where(and_(
                #     self.GRANTS.columns.secondaryUserID == item['secondaryUserID'],
                #     self.GRANTS.columns.minFrequency == item["minFrequency"],
                #     self.GRANTS.columns.maxFrequency == item["maxFrequency"],
                #     self.GRANTS.columns.startTime == item['startTime']
                # ))
                # rows = self._execute_query(query)
                #
                # if len(rows) < 1:
                #     grantResponse = WinnForum.GrantResponse()
                #     grantResponse.response = self.algorithms.generateResponse(103)
                #     grantResponse.response.responseData = \
                #         "Grant Request data not committed to DB. Please contact an administrator"

                # grantResponse.grantId = rows[0]['grantId']
                # grant = WinnForum.Grant(
                #     grantResponse.grantId, item["cbsdId"], grantResponse.operationParam,
                #     vtgp, grantResponse.grantExpireTime
                # )  # TODO: Check if this can be returned

                responseArr.append(grantResponse.asdict())

        return {
            "status": 1,
            "message": "Grants have been processed",
            "grantResponse": responseArr
        }

    def heartbeat_request(self, data):
        heartbeatArr, grantArr = [], []

        for heartbeat in data["heartbeatRequest"]:
            cbsd = self.nodeCtrl.get_cbsd_by_id(heartbeat['cbsdId'])
            grant = self.get_grant_with_id(heartbeat['grantId'])

            if heartbeat["measReport"]:
                for rpmr in heartbeat["measReport"]["rcvdPowerMeasReports"]:
                    # TODO: check to see if frequency range already exists as a submission
                    #  from specific CBSD to prevent spamming
                    mr = Utilities.measReportObjectFromJSON(rpmr)
                    self.rem.measReportToSASREMObject(mr, cbsd)

            response = self.algorithms.runHeartbeatAlgorithm(
                self.get_grants()['spectrumGrants'], self.rem, heartbeat, grant
            )
            grant.heartbeatTime = datetime.now(timezone.utc)
            grant.heartbeatInterval = response.heartbeatInterval
            grantArr.append(grant)
            heartbeatArr.append(response.asdict())

        return {
                   'status': 0,
                   "heartbeatResponse": heartbeatArr
               }, grantArr

    def relinquishment_request(self, data):
        relinquishArr = []

        for relinquishmentRequest in data["relinquishmentRequest"]:
            if relinquishmentRequest["cbsdId"] is None or relinquishmentRequest["grantId"] is None:
                response = {"response": Utilities.generateResponse(102)}
            else:
                if self.cancel_grant_for_cbsd(
                        relinquishmentRequest["cbsdId"], relinquishmentRequest["grantId"], True
                ):
                    response = {
                        "cbsdId": relinquishmentRequest["cbsdId"],
                        "grantId": relinquishmentRequest["grantId"],
                        "response": Utilities.generateResponse(0)
                    }
                else:
                    response = {"response": Utilities.generateResponse(103)}

            relinquishArr.append(response)

        return {"relinquishmentResponse": relinquishArr}

    def cancel_grants_for_cbsd(self, cbsdId):
        query = delete(self.GRANTS).where(self.GRANTS.columns.cbsdId == cbsdId)
        rows = self._execute_query(query)

        rows = self._execute_query(
            select(self.GRANTS).where(self.GRANTS.columns.cbsdId == cbsdId)
        )
        if rows:
            raise Exception("Associated Grants could not be removed")

    def cancel_grant_for_cbsd(self, cbsdId, grantId, force=False):
        rows = self._execute_query(
            select([self.GRANTS]).where(and_(
                self.GRANTS.columns.grantId == grantId,
                self.GRANTS.columns.cbsdId == cbsdId,
            ))
        )

        if rows:
            self.cancel_grant_by_grantId(rows[0], force)
            return True

        else:
            return False

    def cancel_grant_by_grantId(self, grant, force=False):
        now = datetime.now(timezone.utc)
        grant_startTime = datetime.strptime(grant['startTime'], "%Y-%m-%dT%H:%M").astimezone(pytz.UTC)

        if grant_startTime + timedelta(0, self.algorithms.defaultHeartbeatInterval) < now or force:
            # query = delete(self.GRANTS).where(and_(
            #     self.GRANTS.columns.grantId == grant['grantId'],
            #     self.GRANTS.columns.secondaryUserID == grant['secondaryUserID']
            # ))
            query = delete(self.GRANTS).where(self.GRANTS.columns.grantId == grant['grantId'])
            rows = self._execute_query(query)

            print(f"Grant {grant['grantId']} has been cancelled")

    def spectrumData(self, payload):
        cbsd = self.nodeCtrl.get_cbsd_by_id(payload["spectrumData"]["cbsdId"])
        if cbsd:
            deviceInfo = payload["spectrumData"]
            cbsd.latitude = deviceInfo["latitude"]
            cbsd.longitude = deviceInfo["longitude"]

            if 'spectrumData' in deviceInfo and 'rcvdPowerMeasReports' in deviceInfo['spectrumData']:
                for rpmr in deviceInfo['spectrumData']['rcvdPowerMeasReports']:
                    self.rem.measReportToSASREMObject(Utilities.measReportObjectFromJSON(rpmr), cbsd)
