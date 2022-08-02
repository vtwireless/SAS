import Server_WinnForum as WinnForum
import CBSD


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

    @staticmethod
    def removeGrant(grantId, cbsdId, grants):
        for g in grants:
            if str(g.id) == str(grantId) and str(g.cbsdId) == str(cbsdId):
                grants.remove(g)
                return True
        return False

    @staticmethod
    def loadGrantFromJSON(grantJson):
        ofr = WinnForum.FrequencyRange(
            grantJson["frequency"],
            grantJson["frequency"] + grantJson["bandwidth"]
        )
        operationParam = WinnForum.OperationParam(grantJson["requestPowerLevel"], ofr)
        vtgp = WinnForum.VTGrantParams(
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
        )

        try:
            vtgp.minFrequency = grantJson["requestMinFrequency"]
            vtgp.maxFrequency = grantJson["requestMaxFrequency"]
            vtgp.startTime = grantJson["startTime"]
            vtgp.endTime = grantJson["endTime"]
            vtgp.approximateByteSize = grantJson["requestApproximateByteSize"]
            vtgp.dataType = grantJson["dataType"]
            vtgp.powerLevel = grantJson["requestPowerLevel"]
            vtgp.location = grantJson["requestLocation"]
            vtgp.mobility = grantJson["requestMobility"]
            vtgp.maxVelocity = grantJson["requestMaxVelocity"]
        except KeyError:
            raise Exception('VTGP Params not found')

        grant = WinnForum.Grant(grantJson["grantID"], grantJson["secondaryUserID"], operationParam, vtgp)

        return grant

    @staticmethod
    def loadCBSDFromJSON(json):
        # TODO: Handle null exception
        locArr = json["location"].split(",")
        longitude = locArr[0]
        latitude = locArr[0]

        return CBSD.CBSD(
            json["id"], json["trustLevel"], json["fccId"], json["name"], longitude, latitude, json["IPAddress"],
            json["minFrequency"], json["maxFrequency"], json["minSampleRate"], json["maxSampleRate"], json["cbsdType"],
            json["mobility"], json["status"], json["cbsdSerialNumber"], json["callSign"], json["cbsdCategory"],
            json["cbsdInfo"], json["airInterface"], json["installationParam"], json["measCapability"],
            json["groupingParam"]
        )
