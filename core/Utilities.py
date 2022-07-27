import Server_WinnForum as WinnForum


class Utilities:
    def __init__(self):
        pass

    @staticmethod
    def generateResponse(responseCode):
        return {
            "responseCode": str(responseCode),
            "message": WinnForum.responseDecode(responseCode)
        }

    @staticmethod
    def measReportObjectFromJSON(json):
        return WinnForum.RcvdPowerMeasReport(
            float(json["measFrequency"]),
            json["measBandwidth"],
            json["measRcvdPower"] or 0
        )

    @staticmethod
    def initiateSensing(lowFreq, highFreq, allRadios):
        count, radioCountLimit = 0, 3
        radiosToChangeBack, radiosToCommunicate = [], []

        for radio in allRadios:
            if not radio.justChangedParams:
                changeParams = dict(
                    lowFrequency=lowFreq,
                    highFrequency=highFreq,
                    cbsdId=radio.cbsdId
                )
                radio.justChangedParams = True
                radiosToChangeBack.append(radio)
                radiosToCommunicate.append({'data': changeParams, 'room': radio.sid})
                count += 1

            if count >= radioCountLimit or count > len(allRadios) / 3:
                # don't use more than 1/3 of the radios to check band
                break

        return radiosToChangeBack, radiosToCommunicate

    @staticmethod
    def resetRadioStatuses(radios):
        for radio in radios:
            radio.justChangedParams = False

