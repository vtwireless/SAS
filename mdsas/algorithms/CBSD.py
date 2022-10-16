#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBSD CLASS OBJECT FILE
"""


class CBSD:
    """
    Grant - Array of DeregistrationResponsedata objects.
        Each DeregistrationResponse data object represents a deregistrationresponse to a deregistration request of a
        CBSD

    Attributes
    ----------
    cbsdId : string (conditional)
        This parameter is included if and only if the cbsdId parameter in the DeregistrationRequestobject contains a
        valid CBSD identity.
        If included, the SAS shall set this parameterto the value of the cbsdIdparameter in the corresponding
        DeregistrationRequest object.
    response : object Response (required)
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for
        a reason.  See Table 14: ResponseObject Definition
    """

    def __init__(self, id, trustLevel, fccId, name=None, longitude=None, latitude=None, IPAddress=None,
                 minFreq=None, maxFreq=None, minSR=None, maxSR=None, type=None, mobility=False, status=None,
                 comment=None, cbsdSerialNumber=None, callSign=None, cbsdCategory="A", cbsdInfo="", airInterface=None,
                 installationParam=None, measCapability=None, groupingParam=None, fullyTrusted=False, userId=None,
                 tierClassID=None):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.trustLevel = trustLevel
        self.longitude = longitude
        self.latitude = latitude
        self.trustLevel = trustLevel
        self.IPAddress = IPAddress
        self.minFrequency = minFreq
        self.maxFrequency = maxFreq
        self.minSampleRate = minSR
        self.maxSampleRate = maxSR
        self.nodeType = type
        self.mobility = mobility
        self.status = status
        self.comment = comment
        self.fccId = fccId
        self.cbsdSerialNumber = cbsdSerialNumber
        self.callSign = callSign
        self.cbsdCategory = cbsdCategory
        self.cbsdInfo = cbsdInfo
        self.airInterface = airInterface
        self.installationParam = installationParam
        self.measCapability = measCapability
        self.groupingParam = groupingParam
        self.fullyTrusted = fullyTrusted
        self.userId = userId
        self.tierClassID = tierClassID

    def asdict(self):
        return_dict = {}
        if self.id:
            return_dict["id"] = self.id
        if self.name:
            return_dict["name"] = self.name
        if self.latitude:
            return_dict["latitude"] = self.latitude
        if self.longitude:
            return_dict["longitude"] = self.longitude
        if self.trustLevel:
            return_dict["trustLevel"] = self.trustLevel
        if self.longitude:
            return_dict["longitude"] = self.longitude
        if self.latitude:
            return_dict["latitude"] = self.latitude
        if self.trustLevel:
            return_dict["trustLevel"] = self.trustLevel
        if self.IPAddress:
            return_dict["IPAddress"] = self.IPAddress
        if self.minFrequency:
            return_dict["minFrequency"] = self.minFrequency
        if self.maxFrequency:
            return_dict["maxFrequency"] = self.maxFrequency
        if self.minSampleRate:
            return_dict["minSampleRate"] = self.minSampleRate
        if self.maxSampleRate:
            return_dict["maxSampleRate"] = self.maxSampleRate
        if self.nodeType:
            return_dict["nodeType"] = self.nodeType
        if self.mobility:
            return_dict["mobility"] = self.mobility
        if self.status:
            return_dict["status"] = self.status
        if self.comment:
            return_dict["comment"] = self.comment
        if self.fccId:
            return_dict["fccId"] = self.fccId
        if self.cbsdSerialNumber:
            return_dict["cbsdSerialNumber"] = self.cbsdSerialNumber
        if self.callSign:
            return_dict["callSign"] = self.callSign
        if self.cbsdCategory:
            return_dict["cbsdCategory"] = self.cbsdCategory
        if self.cbsdInfo:
            return_dict["cbsdInfo"] = self.cbsdInfo
        if self.airInterface:
            return_dict["airInterface"] = self.airInterface
        if self.installationParam:
            return_dict["installationParam"] = self.installationParam
        if self.measCapability:
            return_dict["measCapability"] = self.measCapability
        if self.groupingParam:
            return_dict["groupingParam"] = self.groupingParam
        if self.fullyTrusted:
            return_dict["fullyTrusted"] = self.fullyTrusted
        if self.userId:
            return_dict["userId"] = self.userId
        if self.tierClassID:
            return_dict["tierClassID"] = self.tierClassID
        return return_dict
