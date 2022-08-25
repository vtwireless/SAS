import threading

import sqlalchemy as db
from sqlalchemy import select, and_, insert, delete, update
from sqlalchemy.engine import CursorResult

from settings import settings
from Utilities import Utilities
from algorithms import SASREM
from algorithms import Server_WinnForum as WinnForum
from controllers.CBSDController import CBSDController


class GrantController:
    GRANTS = None

    def __init__(self, metadata, engine, connection, algorithms, nodeCtrl):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms = algorithms
        self.nodeCtrl: CBSDController = nodeCtrl
        self.rem = SASREM.SASREM()

        self._set_grants_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def _set_grants_table(self):
        self.GRANTS = db.Table(
            settings.GRANT_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    def get_grants(self):
        query = select([self.GRANTS])
        try:
            rows = self._execute_query(query)

            return {
                'status': 1,
                'spectrumGrants': rows
            }
        except Exception as err:
            raise Exception(str(err))

    def get_grant_with_id(self, grantId):
        query = select([self.GRANTS]).where(
            self.GRANTS.columns.grantId == grantId
        )
        rows = self._execute_query(query)

        if len(rows) == 0:
            raise Exception(f"Grant with Id {grantId} not found")
        else:
            return Utilities.loadGrantFromJSON(rows[0])

    def spectrum_inquiry(self, data):
        inquiryArr = []
        radiosToChangeBack = []
        radiosToCommunicate = []

        for request in data["spectrumInquiryRequest"]:
            response = WinnForum.SpectrumInquiryResponse(
                request["cbsdId"], [], self.algorithms.generateResponse(0)
            )

            for fr in request["inquiredSpectrum"]:
                lowFreq, highFreq = int(fr["lowFrequency"]), int(fr["highFrequency"])
                channelType, ruleApplied = "PAL", "FCC_PART_96"
                maxEirp = self.algorithms.getMaxEIRP()

                if self.algorithms.acceptableRange(lowFreq, highFreq):
                    if 3700000000 > highFreq > 3650000000:
                        channelType = "GAA"

                    present = self.algorithms.isPUPresentREM(
                        self.rem, highFreq, lowFreq, None, None, None
                    )
                    if present == 0:  # No PU is present
                        fr = WinnForum.FrequencyRange(lowFreq, highFreq)
                        availChan = WinnForum.AvailableChannel(fr, channelType, ruleApplied, maxEirp)
                        response.availableChannel.append(availChan)

                    elif present == 2:  # Spectrum Data not available
                        rTCB, rTC = self.initiateSensing(lowFreq, highFreq)
                        radiosToChangeBack.extend(rTCB)
                        radiosToCommunicate.extend(rTC)

                    # TODO: present == 1  # PU is present?

            inquiryArr.append(response.asdict())

        threading.Timer(
            3.0, self.resetRadioStatuses, [radiosToChangeBack]
        ).start()

        return {
            'status': 0,
            "spectrumInquiryResponse": inquiryArr
        }, radiosToCommunicate

    def initiateSensing(self, lowFreq, highFreq):
        count, radioCountLimit = 0, 3
        radiosToChangeBack, radiosToCommunicate = [], []

        allRadios = self.nodeCtrl.get_cbsd()
        for radio in allRadios:
            if not radio.justChangedParams:
                changeParams = dict(
                    lowFrequency=lowFreq,
                    highFrequency=highFreq,
                    cbsdId=radio.cbsdID
                )
                radio.justChangedParams = True
                radiosToChangeBack.append(radio)
                radiosToCommunicate.append({'data': changeParams, 'room': radio.sid})
                count += 1

            if count >= radioCountLimit or count > len(allRadios) / 3:
                # don't use more than 1/3 of the radios to check band
                break

        return radiosToChangeBack, radiosToCommunicate

    def resetRadioStatuses(self, radios):
        for radio in radios:
            self.nodeCtrl.update_cbsd_justChangedParams(radio.cbsdID, False)
