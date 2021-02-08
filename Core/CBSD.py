#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBSD CLASS OBJECT FILE
"""

class CBSD:
	"""
	Grant - Array of DeregistrationResponsedata objects.
		Each DeregistrationResponse data object represents a deregistrationresponse to a deregistration request of a CBSD
	
	Attributes
	----------
	cbsdId : string (conditional)
		This parameter is included if and only if the cbsdId parameter in the DeregistrationRequestobject contains a valid CBSD identity.
		If included, the SAS shall set this parameterto the value of the cbsdIdparameter in the corresponding DeregistrationRequest object.

	response : object Response (required)
		This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a reason.  See Table 14: ResponseObject Definition
	"""
	def __init__(self, id, trustLevel, fccId, name=None, longitude=None, latitude=None, IPAddress=None, \
		minFreq=None, maxFreq=None, minSR=None, maxSR=None, type=None, mobility=False, status=None, \
			 comment=None, cbsdSerialNumber=None, callSign=None, cbsdCategory="A", cbsdInfo="", airInterface=None, \
				installationParam=None, measCapability=None, groupingParam=None):
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
		self.cbsdCategroy = cbsdCategory
		self.cbsdInfo = cbsdInfo
		self.airInterface = airInterface
		self.installationParam = installationParam
		self.measCapability = measCapability
		self.groupingParam = groupingParam

	def asdict(self):
		return_dict = {}
		return_dict["id"] = self.id
		if(self.cbsdId):
			return_dict["cbsdId"] = self.cbsdId
		if(self.operationParam):
			return_dict["operationParam"] = self.operationParam.asdict()
		if(self.vtGrantParams):
			return_dict["vtGrantParams"] = self.vtGrantParams.asdict()
		return return_dict
