import random

import algorithms.Server_WinnForum as WinnForum
import algorithms.CBSD as CBSD
from algorithms.SASAlgorithms import SASAlgorithms


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
            json['cbsdID'], json["trustLevel"], json["fccId"], json['nodeName'], longitude, latitude, json["IPAddress"],
            json["minFrequency"], json["maxFrequency"], json["minSampleRate"], json["maxSampleRate"], json['nodeType'],
            json["mobility"], json["status"], json["cbsdSerialNumber"], json["callSign"], json["cbsdCategory"],
            json["cbsdInfo"], json["airInterface"], json["installationParam"], json["measCapability"],
            json["groupingParam"], userId=json["userId"], tierClassID=json["tierClassID"]
        )

    @staticmethod
    def getRandBool():
        """Randomly returns True or False"""
        return bool(random.getrandbits(1))  # Requires import random

    @staticmethod
    def getChannelFromFrequency(freq):
        """Returns the lowFreq for the channel 'freq' can be found"""
        NUM_OF_CHANNELS = 15

        for channel in range(NUM_OF_CHANNELS):
            if freq < ((channel + 1) * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ:
                return channel
        return None

    @staticmethod
    def getChannelFreqFromChannel(channel, getHighFreq=False):
        """Convert a channel integer to a freq for the channel"""
        if getHighFreq:
            channel = channel + 1

        return (channel * SASAlgorithms.TENMHZ) + SASAlgorithms.MINCBRSFREQ

    @staticmethod
    def double_pad_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus):
        """Executes Double Pad Obfuscation Scheme"""
        obfuscationArr = []
        pu_bw = puHighFreq - puLowFreq
        low_su_low_freq = puLowFreq - pu_bw
        low_su_high_freq = puLowFreq
        high_su_low_freq = puHighFreq
        high_su_high_freq = puHighFreq + pu_bw

        if Utilities.getRandBool():  # Randomly pick to pad top or bottom first
            if low_su_low_freq >= SASAlgorithms.MINCBRSFREQ and est_num_of_available_sus:
                obfuscationArr.append((low_su_low_freq, low_su_high_freq))
                est_num_of_available_sus -= 1

            if high_su_high_freq <= SASAlgorithms.MAXCBRSFREQ and est_num_of_available_sus:
                obfuscationArr.append((high_su_low_freq, high_su_high_freq))
                est_num_of_available_sus -= 1
        else:
            if high_su_high_freq <= SASAlgorithms.MAXCBRSFREQ:
                obfuscationArr.append((high_su_low_freq, high_su_high_freq))
                est_num_of_available_sus -= 1

            if low_su_low_freq >= SASAlgorithms.MINCBRSFREQ:
                obfuscationArr.append((low_su_low_freq, low_su_high_freq))
                est_num_of_available_sus -= 1

        return obfuscationArr

    @staticmethod
    def fill_channel_obfuscate(puLowFreq, puHighFreq, est_num_of_available_sus):
        """Fills PU Occupied Channel(s)"""
        obfuscationArr = []

        # Find the channel where the lowest PU frequency resides
        puLowChannel = Utilities.getChannelFromFrequency(puLowFreq)
        channelFreqLow = Utilities.getChannelFreqFromChannel(puLowChannel)
        lowCbsdBw = puLowFreq - channelFreqLow

        # Find the channel where the highest PU frequency resides
        puHighChannel = Utilities.getChannelFromFrequency(puHighFreq)
        channelFreqHigh = Utilities.getChannelFreqFromChannel(puHighChannel, getHighFreq=True)
        highCbsdBw = channelFreqHigh - puHighFreq

        # Only command radio if the obfuscating spectrum is at least 1 kHz
        if highCbsdBw > 1000:
            obfuscationArr.append((puHighFreq, channelFreqHigh))

        if lowCbsdBw >= 1000:
            obfuscationArr.append((channelFreqLow, puLowFreq))

        return obfuscationArr


