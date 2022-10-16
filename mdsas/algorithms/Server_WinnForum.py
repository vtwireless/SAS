#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class file containing objects as specified beginning Page 34 of the following pdf:
https://winnf.memberclicks.net/assets/CBRS/WINNF-TS-0016.pdf
Document Version: V1.2.5

Revised: November 14, 2020
Authored by: Cameron Makin (cammakin8@vt.edu), Joseph Tolley (jtolley@vt.edu)
Advised by Carl Dietrich (cdietric@vt.edu)
For Wireless@VT

Notes:
[1] Valid measReportConfig strings: 
RECEIVED_POWER_WITHOUT_GRANT
RECEIVED_POWER_WITH_GRANT
INDOOR_LOSS_USING_GNSS
"""
from typing import List


def _ensureIsList(param):
    """
    Ensures the passed parameter is an array, even if it is one element 
        Parameters: 
            param (any data type): parameter to check if is an array
        Returns:
            param: list/array ensuredv version of "param" originally passed in
    """
    if not isinstance(param, list):
        return [param]
    else:
        return param


def _toJsonDictArray(obj_arr):
    """
    Returns an array of dictonary elements in JSON format.
    Used when an object as an attribute that is an array of Objects.
    Arary of Objects must be passed to this to return a JSON friendly datatype. 
        Parameters: 
            obj_arr (Array of Objects): array of Objects that *MUST HAVE METHOD "asdict()"*
        Returns:
            dict_arr: Array with dictonary elements
    """
    dict_arr = []
    for obj in obj_arr:
        dict_arr.append(obj.asdict())
    return dict_arr


def responseDecode(code):
    """
    Helper function to decode the values of responceCode into their Name
        Parameters:
            code (integer): code provided to translate into error name
        Returns:
            name (string): name belonging to provided code
    """
    if code == 0:
        return "SUCCESS"
    elif code == 100:
        return "VERSION"
    elif code == 101:
        return "BLACKLISTED"
    elif code == 102:
        return "MISSING_PARAM"
    elif code == 103:
        return "INVALID_VALUE"
    elif code == 104:
        return "CERT_ERROR"
    elif code == 105:
        return "DEREGISTER"
    elif code == 200:
        return "REG_PENDING"
    elif code == 201:
        return "GROUP_ERROR"
    elif code == 300:
        return "UNSUPPORTED_SPECTRUM"
    elif code == 200:
        return "INTERFERENCE"
    elif code == 401:
        return "GRANT_CONFLICT"
    elif code == 500:
        return "TERMINATED_GRANT"
    elif code == 501:
        return "SUSPENDED_GRANT"
    elif code == 501:
        return "UNSYNC_OP_PARAM"
    else:
        return "INVALID_CODE"


class RegistrationRequest:
    """
    A Registration Request requires an array of these RegistrationRequest data objects. 
    Each RegistrationRequest data object represents a registration request of a CBSD.
    
    Attributes
    ----------
    userId : string (required)
        The UR-ID per [n.12] R2-SRR-02 conformant per section 2.2 of [n.18].
    fccId : string (required)
        The FCC certification identifier of the CBSD. 
        It is a string of up to 19 characters as described in [n.22].
    cbsdSerialNumber : string (required)
        A serial number assigned to the CBSD by the CBSD device manufacturer having a maximum length of 64 octets.
        This serial number shall be unique for every CBSD instance sharing the same value of fccId. 
        Each CBSD has a single CBSD Antenna (Ref. definition in section 4) and has a single cbsdSerialNumber.
    callSign : string (optional)
         A device identifier provided by the FCC per [n.13].
         NOTE: This parameter is for further study.
    cbsdCategory : string (conditional)
        Device Category of the CBSD. 
        Allowed values are "A" or "B" as defined in Part 96.
        
    cbsdInfo : object CbsdInfo (optional)
        Information about this CBSD model.
    airInterface : object AirInterface (conditional)
        A data object that includes information on the air interface technology of the CBSD. 
    installationParam : object InstallationParam (conditional)
        A data object that includes information on CBSD installation. 
    measCapability : array of string (conditional)
        The array of string lists measurement reporting capabilities of the CBSD.
        The permitted enumerations are specified in [n.21].
    groupingParam : array of object GroupParam (optional)
        An array of data objects that includes information on CBSD grouping
    cpiSignatureData : object CpiSignatureData (optional)
        The CPI is vouching for the parameters included in this object.
        In addition, the digital signature for these parameters is included.
    vtParams : object VTParams (optional)
        Object used for research data collection.
        This is not a WinnForum specified data type.    
    """

    def __init__(self, userId, fccId,
                 cbsdSerialNumber, callSign=None, cbsdCategory=None,
                 cbsdInfo=None, airInterface=None, installationParam=None,
                 measCapability=None, groupingParam=None, cpiSignatureData=None, vtParams=None, trustScore=None,
                 fullyTrusted=None):

        self.userId = userId  # R
        self.fccId = fccId  # R
        self.cbsdSerialNumber = cbsdSerialNumber  # R
        self.callSign = callSign  # O
        self.cbsdCategory = cbsdCategory  # C
        self.cbsdInfo = cbsdInfo  # O
        self.airInterface = airInterface  # C
        self.installationParam = installationParam  # C
        self.measCapability = _ensureIsList(measCapability)  # C
        self.groupingParam = _ensureIsList(groupingParam)  # O
        self.cpiSignatureData = cpiSignatureData  # O
        self.vtParams = vtParams  # O
        self.trustScore = trustScore  # O
        self.fullyTrusted = fullyTrusted  # O

    def asdict(self):
        return_dict = {}
        if self.userId:
            return_dict["userId"] = self.userId
        if self.fccId:
            return_dict["fccId"] = self.fccId
        if self.cbsdSerialNumber:
            return_dict["cbsdSerialNumber"] = self.cbsdSerialNumber
        if self.callSign:
            return_dict["callSign"] = self.callSign
        if self.cbsdCategory:
            return_dict["cbsdCategory"] = self.cbsdCategory
        if self.cbsdInfo:
            return_dict["cbsdInfo"] = self.cbsdInfo.asdict()
        if self.airInterface:
            return_dict["airInterface"] = self.airInterface.asdict()
        if self.installationParam:
            return_dict["installationParam"] = self.installationParam.asdict()
        if self.measCapability:
            return_dict["measCapability"] = self.measCapability
        if self.groupingParam[0]:
            return_dict["groupingParam"] = _toJsonDictArray(self.groupingParam)
        if self.cpiSignatureData:
            return_dict["cpiSignatureData"] = self.cpiSignatureData.asdict()
        if self.vtParams:
            return_dict["vtParams"] = self.vtParams.asdict()
        if self.trustScore:
            return_dict["trustScore"] = self.trustScore
        if self.fullyTrusted:
            return_dict["fullyTrusted"] = self.fullyTrusted
        return return_dict


class AirInterface:
    """
        Object that includes info on the air interface technology of the CBSD
        Attributes
        ----------
        radioTechnology : string (conditional)
            This parameter specifies the radio access technology that the CBSD uses for operation in the CBRS band. 
            The permitted values are specified in [n.21].
        """

    def __init__(self, radioTechnology=None):
        self.radioTechnology = radioTechnology  # C

    def asdict(self):
        return_dict = {}
        if self.radioTechnology:
            return_dict["radioTechnology"] = self.radioTechnology
        return return_dict


class InstallationParam:
    """
    InstallationParam - A data object that includes information on CBSD installation.
    
    Attributes
    ----------
    latitude : number (conditional)
        Latitude of the CBSD antenna locationin degrees relative to the WGS 84 datum [n.11]. 
        The allowed range is from -90.000000 to +90.000000.  
        Positive values represent latitudes north of the equator; negative values south of the equator.  
        Values are specified using 6 digits to the right of the decimal point.
        Note: Use of WGS84 will also satisfy the NAD83 positioning requirements for CBSDs with the accuracy specified
        by Part 96 [n.8].
        For reporting the CBSD location to the FCC, the SAS is responsible for converting coordinates from the WGS84
        datum to the NAD83 datum.
    longitude : number (conditional)
        Longitude of the CBSD antennalocationin degrees relative to the WGS84 datum [n.11]. 
        The allowed range is from -180.000000 to +180.000000.
        Positive values represent longitudes east of the prime meridian; negative values west of the prime meridian.
        Values are specified using 6 digits to the right of the decimal point.
        Note: Use of WGS84 will also satisfy the NAD83 positioning requirements for CBSDs with the accuracy specified
        by Part 96 [n.8].
        For reporting the CBSD location to the FCC, the SAS is responsible for converting coordinates from theWGS84
        datum to the NAD83 datum.
    height : number (conditional)
        The CBSD antenna height in meters.
        When the heightType parameter value is "AGL", the antenna height should be given relative to ground level.
        When the heightTypeparameter value is "AMSL", it is given with respect to WGS84 datum.
        For reporting the CBSD location to the FCC, the SAS is responsible for converting coordinates from the WGS84
        datum to the NAD83 datum.
    heightType : string (conditional)
        The value should be "AGL" or "AMSL". 
        AGL height is measured relative to the ground level.
        AMSL height is measured relative to the mean sea level.
    horizontalAccuracy : number (optional)
        A positive number in meters to indicate accuracy of the CBSD antenna horizontal location.
        This optional parameter should only be present if its value is less than the FCC requirement of 50 meters.
    verticalAccuracy : number (optional)
        A positive number in meters to indicate accuracy of the CBSD antennavertical location. 
        This optional parameter should only be present if its value is less than the FCC requirement of 3 meters.
    indoorDeployment : boolean (conditional)
        Whether the CBSD antenna is indoor or not.
        True: indoor. 
        False: outdoor.
    antennaAzimuth : number (conditional)
        Boresight direction of the horizontal plane of the antenna in degrees with respect to true north.
        The value of this parameter is an integer with a value between 0 and 359 inclusive.
        A value of 0 degrees means true north; a value of 90 degrees means east. 
        This parameter is optional for Category A CBSDs and REG-conditional for Category B CBSDs
    antennaDowntilt : number (conditional)
        Antenna down tilt in degrees and is an integer with a value between -90 and +90 inclusive; 
            a negative value means the antenna is tilted up (above horizontal).
        This parameter is optional for Category A CBSDs and REG-conditional for Category B CBSDs
    antennaGain : number (conditional)
        Peak antenna gain in dBi.
        This parameter is an integer with a value between -127 and +128 (dBi) inclusive.
    eirpCapability : number (optional)
        This parameter is the maximum EIRP in units of dBm/10MHz to be used by this CBSD and shall be no more than the
        rounded-up FCC certified maximum EIRP.
        The Value of this parameter is an integer with a value between -127 and +47 (dBm/10MHz) inclusive.
        If not included, SAS shall set eirpCapabilityas the rounded up FCC certified maximum EIRPof the CBSD.
    antennaBeamwidth : number (conditional)
        3-dB antenna beamwidth of the antenna in the horizontal-plane in degrees.
        This parameter is an unsigned integer having a value between 0 and 360 (degrees) inclusive; 
            it is optional for Category A CBSDs and REG-conditional for category B CBSDs.
        Note: A value of 360 (degrees) means the antenna has an omnidirectional radiation pattern in the horizontal
        plane.
    
    antennaModel : string (optional)
        If an external antenna is used, the antenna model is optionally provided in this field.
        The string has a maximum length of 128 octets.
    """

    def __init__(self, latitude=None, longitude=None, height=None, heightType=None,
                 horizontalAccuracy=None, verticalAccuracy=None, indoorDeployment=None,
                 antennaAzimuth=None, antennaDowntilt=None, antennaGain=None, eirpCapability=None,
                 antennaBeamwidth=None, antennaModel=None):
        self.latitude = latitude  # C
        self.longitude = longitude  # C
        self.height = height  # C
        self.heightType = heightType  # C
        self.horizontalAccuracy = horizontalAccuracy  # O
        self.verticalAccuracy = verticalAccuracy  # O
        self.indoorDeployment = indoorDeployment  # C
        self.antennaAzimuth = antennaAzimuth  # C
        self.antennaDowntilt = antennaDowntilt  # C
        self.antennaGain = antennaGain  # C
        self.eirpCapability = eirpCapability  # O
        self.antennaBeamwidth = antennaBeamwidth  # C
        self.antennaModel = antennaModel  # O

    def asdict(self):
        return_dict = {}
        if self.latitude:
            return_dict["latitude"] = self.latitude
        if self.longitude:
            return_dict["longitude"] = self.longitude
        if self.height:
            return_dict["height"] = self.height
        if self.heightType:
            return_dict["heightType"] = self.heightType
        if self.horizontalAccuracy:
            return_dict["horizontalAccuracy"] = self.horizontalAccuracy
        if self.verticalAccuracy:
            return_dict["verticalAccuracy"] = self.verticalAccuracy
        if self.indoorDeployment:
            return_dict["indoorDeployment"] = self.indoorDeployment
        if self.antennaAzimuth:
            return_dict["antennaAzimuth"] = self.antennaAzimuth
        if self.antennaDowntilt:
            return_dict["antennaDowntilt"] = self.antennaDowntilt
        if self.antennaGain:
            return_dict["antennaGain"] = self.antennaGain
        if self.eirpCapability:
            return_dict["eirpCapability"] = self.eirpCapability
        if self.antennaBeamwidth:
            return_dict["antennaBeamwidth"] = self.antennaBeamwidth
        if self.antennaModel:
            return_dict["antennaModel"] = self.antennaModel
        return return_dict


class GroupParam:
    """
    GroupParam - incldude information on CBSD grouping
    Attributes
    ----------
    groupType : string (required)
        Enumeration field describing the type of group this group ID describes.
        The following are permitted enumerations: "INTERFERENCE_COORDINATION".
    groupId : string (required)
        This field specifies the identifier for this group of CBSDs. 
        When the groupType is set to "INTERFERENCE_COORDINATION", the namespace for groupId is userId.
    """

    def __init__(self, groupType, groupId):
        self.groupType = groupType  # R
        self.groupId = groupId  # R

    def asdict(self):
        return_dict = {}
        if self.groupType:
            return_dict["groupType"] = self.groupType
        if self.groupId:
            return_dict["groupId"] = self.groupId
        return return_dict


class CbsdInfo:
    """
    CbsdInfo - The CbsdInfo object can be extended with other vendor information in additional key-value pairs.
    
    Attributes
    ----------
    vendor : string (optional)
        The name of the CBSD vendor.
        The maximum length of this string is 64 octets.
    model : string (optional)
        The name of the CBSD model.
        The maximum length of this string is 64 octets.
    softwareVersion : string (optional)
        Software version of this CBSD.
        The maximum length of this string is 64 octets.
    hardwareVersion : string (optional)
        Hardware version of this CBSD.
        The maximum length of this string is 64 octets.
    firmwareVersion : string (optional)
        Firmware version of this CBSD.
        The maximum length of this string is 64 octets.
    """

    def __init__(self, vendor=None, model=None, softwareVersion=None,
                 hardwareVersion=None, firmwareVersion=None):
        self.vendor = vendor  # O
        self.model = model  # O
        self.softwareVersion = softwareVersion  # O
        self.hardwareVersion = hardwareVersion  # O
        self.firmwareVersion = firmwareVersion  # O

    def asdict(self):
        return_dict = {}
        if self.vendor:
            return_dict["vendor"] = self.vendor
        if self.model:
            return_dict["model"] = self.model
        if self.softwareVersion:
            return_dict["softwareVersion"] = self.softwareVersion
        if self.hardwareVersion:
            return_dict["hardwareVersion"] = self.hardwareVersion
        if self.firmwareVersion:
            return_dict["firmwareVersion"] = self.firmwareVersion
        return return_dict


class CpiSignatureData:
    """
    CpiSignatureData - Note: The JOSE JSON Web Signature per RFC-7515(see [n.19]) is used to ensure data integrity 
        and CPI non-repudiation of the signed parameters.
        The JOSE compact serialization is formed by concatenating the protectedHeader, encodedCpiSignedData, and 
        digitalSignaturefields with "." Characters, as described in section 3 of RFC 7515[n.19].
    Attributes
    ----------
    protectedHeader : string (required)
        The value of this parameter is the BASE64-encoded JOSE protected header. 
        This is a JSON object equivalent to the JWT RS256 method or the ES256 method described in RFC 7515 [n.19]
        Section 3.
        BASE64 encoding is per RFC 4648 (see [n.20]).
        Valid values are equivalent to the JSON:{ "typ": "JWT", "alg": "RS256" } or  { "typ": "JWT", "alg": "ES256" }
    encodedCpiSignedData : string (required)
        The value of this parameter is the encoded JOSE payload data to be signed by the CPI’s private key.
        This parameter is calculated by taking the BASE64 encoding of a CpiSignedDataobject (see Table 10) according
        to the procedures in RFC 7515[n.19], Section 3.
    digitalSignature : string (required)
        The value of this parameter is the CPI digital signature applied to the encodedCpiSignedData field.
        This signature is the BASE64URL encoding of the digital signature, prepared according to the procedures in RFC
        7515 [n.19] Section 3, using the algorithm as declared in the protectedHeaderfield.
    """

    def __init__(self, protectedHeader, encodedCpiSignedData, digitalSignature):
        self.protectedHeader = protectedHeader  # R
        self.encodedCpiSignedData = encodedCpiSignedData  # R
        self.digitalSignature = digitalSignature  # R

    def asdict(self):
        return_dict = {}
        if self.protectedHeader:
            return_dict["protectedHeader"] = self.protectedHeader
        if self.encodedCpiSignedData:
            return_dict["encodedCpiSignedData"] = self.encodedCpiSignedData
        if self.digitalSignature:
            return_dict["digitalSignature"] = self.digitalSignature
        return return_dict


class CpiSignedData:
    """
    CpiSignedData - 
    Attributes
    ----------
    fccId : string (required)
        The value of this parameter is the FCC ID of the CBSD.
        Shall be equal to the fccId parameter value in the enclosing registration request.
    
    cbsdSerialNumber : string (required)
        The value of this parameter is the CBSD serial number.Shallbe equal to the cbsdSerialNumber of the enclosing
        registration request.
    installationParam : object InstallParam (required)
            The value of this parameter is the InstallationParamobject containing the parameters being certified by
            the CPI, and only those.
    
    professionalInstallerData : object ProfessionalInstallerData (required)
        The value of this parameter is the data identifying the CPI vouching for the installation parameters included
        in the installationParamvalue contained in this object.
    """

    def __init__(self, fccId, cbsdSerialNumber, installationParam, professionalInstallerData):
        self.fccId = fccId  # R
        self.cbsdSerialNumber = cbsdSerialNumber  # R
        self.installationParam = installationParam  # R
        self.professionalInstallerData = professionalInstallerData  # R

    def asdict(self):
        return_dict = {}
        if self.fccId:
            return_dict["fccId"] = self.fccId
        if self.cbsdSerialNumber:
            return_dict["cbsdSerialNumber"] = self.cbsdSerialNumber
        if self.installationParam:
            return_dict["installationParam"] = self.installationParam.asdict()
        if self.professionalInstallerData:
            return_dict["professionalInstallerData"] = self.professionalInstallerData.asdict()
        return return_dict


class ProfessionalInstallerData:
    """
    ProfessionalInstallerData - 
    Attributes
    ----------
    cpiId : string (required)
        The value of this parameter is the ID of the CPI providing information to the SAS. This string has a maximum
        length of 256 octets.
    cpiName : string (required)
    The value of this parameter is the human-readable name of the CPI providing information to the SAS. This string
    has a maximum length of 256 octets.
    installCertificationTime : string (required)
        The value of this parameter is the UTC date and time at which the CPI identified in this object certified the
        CBSD’s installed parameters. It is expressed using the format, YYYY-MM-DDThh:mm:ssZ, as defined by [n.7].
    """

    def __init__(self, cpiId, cpiName, installCertificationTime):
        self.cpiId = cpiId  # R
        self.cpiName = cpiName  # R
        self.installCertificationTime = installCertificationTime  # R

    def asdict(self):
        return_dict = {}
        if self.cpiId:
            return_dict["cpiId"] = self.cpiId
        if self.cpiName:
            return_dict["cpiName"] = self.cpiName
        if self.installCertificationTime:
            return_dict["installCertificationTime"] = self.installCertificationTime
        return return_dict


class VTParams:
    """
    VTParams - This object contains parameters regarding the node being registered used for research purposes.
    Attributes
    ----------
    minFrequency : integer (required)
        Minimum receiving frequency
    maxFrequency : integer (required)
        Maximum receiving frequency
    minSampleRate : integer (required)
        Minimum receiving sample rate
    maxSampleRate : integer (required)
        Maximum receiving sample rate
    nodeType : string (required)
        Variable to organize nodes into groups
    isMobile : boolean-string (required)
        Radio has the ability to operate while moving
    """

    def __init__(self, minFrequency, maxFrequency, minSampleRate,
                 maxSampleRate, nodeType, isMobile):
        self.minFrequency = minFrequency
        self.maxFrequency = maxFrequency
        self.minSampleRate = minSampleRate
        self.maxSampleRate = maxSampleRate
        self.nodeType = nodeType if nodeType else "VT-CRTS-Node"
        self.isMobile = isMobile

    def asdict(self):
        return_dict = {}
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
        if self.isMobile:
            return_dict["isMobile"] = self.isMobile
        return return_dict


class Response:
    """
    Response -
    Attributes
    ----------
    responseCode : number (required)
        An integer to indicate the type of result. The value 0 means the corresponding CBSD request is successful.
        This shall be one of the values in Table 39.
    responseMessage : string (optional)
        A short description of the result
    responseData : Dependent on responseCode–see Table 40: responseDataDefinitions. (optional)
        Additional data can be included to help the CBSD resolve failures.
    """

    def __init__(self, responseCode, responseMessage=None, responseData=None):
        self.responseCode = responseCode  # R
        self.responseMessage = responseMessage  # O
        self.responseData = responseData  # O

    def asdict(self):
        return_dict = {}
        if self.responseCode:
            return_dict["responseCode"] = self.responseCode
        if self.responseMessage:
            return_dict["responseMessage"] = self.responseMessage
        if self.responseData:
            return_dict["responseData"] = self.responseData
        return return_dict


class RegistrationResponse:
    """
    RegistrationResponse - This parameter is an array of RegistrationResponse data objects. 
        Each RegistrationResponsedata object represents a registration response to a registration request from a CBSD.
    Attributes
    ----------
    cbsdId : string (conditional)
        This is a CBRS-wide unique identifier for this CBSD. 
        This parameter shall be included if and only if the responseCode indicates SUCCESS. 
        The CBSD shall set its CBSD identity to the value received in this parameter. 
        The string has a maximum length of 256 octets.
    measReportConfig : array of string (optional)
        SAS uses this parameter to configure CBSD measurement reporting. 
        The measurement report requested by SAS shall be consistent with the CBSD measurement capabilities reported
        during the registration request.
        The CBSD shall report the measurement listed in this array. 
        The permitted enumerations arespecified in [n.21].
    response : object Response (required)
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason. See Table 14: ResponseObject Definition.
    """

    def __init__(self, cbsdId=None, measReportConfig=None, response=Response(102)):
        self.cbsdId = cbsdId  # C
        self.measReportConfig = _ensureIsList(measReportConfig)  # O
        self.response: Response = response if response else Response(102)

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.measReportConfig[0]:
            return_dict["measReportConfig"] = self.measReportConfig
        if self.response:
            return_dict["response"] = self.response.asdict()
        return return_dict


class SpectrumInquiryRequest:
    """
    SpectrumInquiryRequest - Array of SpectrumInquiryRequest objects. Each SpectrumInquiryRequest object represents a
    spectrum inquiry request of a CBSD.
    Attributes
    ----------
    cbsdId : string (required)
        The CBSD shall set this parameter to the value of its CBSD identity.
    inquiredSpectrum : array of object FrequencyRange (required)
        This field describes the spectrum for which the CBSD seeks information on spectrum availability.
    measReport : object MeasReport (conditional)
        The CBSD uses this parameter to report measurements to the SAS. The format of the MeasReport object is
        provided in [n.21].
        Refer to section 8 and the measurement capabilities in [n.21] for inclusion rules.
    """

    def __init__(self, cbsdId, inquiredSpectrum, measReport=None):
        self.cbsdId = cbsdId  # R
        self.inquiredSpectrum = _ensureIsList(inquiredSpectrum)  # R
        self.measReport = measReport  # C

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdInfo"] = self.cbsdId
        if self.inquiredSpectrum:
            return_dict["inquiredSpectrum"] = _toJsonDictArray(self.inquiredSpectrum)
        if self.measReport:
            return_dict["measReport"] = self.measReport.asdict()
        return return_dict


class FrequencyRange:
    """fx
    FrequencyRange - 
    Attributes
    ----------
    lowFrequency : number (required)
        The lowest frequency of the frequency range in Hz
    highFrequency : number (required)
        The highest frequency of the frequency range in Hz
    """

    def __init__(self, lowFrequency, highFrequency):
        self.lowFrequency = lowFrequency  # R
        self.highFrequency = highFrequency  # R

    def asdict(self):
        return_dict = {}
        if self.lowFrequency:
            return_dict["lowFrequency"] = self.lowFrequency
        if self.highFrequency:
            return_dict["highFrequency"] = self.highFrequency
        return return_dict


class MeasReport:
    """
    MeasReport - 
    Attibutes
    ---------
    measReports : array of object RcvdPowerMeasReport or IndoorLossGNSSMeasReport (unknown)
         An array of separate reports measured as Received Power.
    """

    def __init__(self, measReports=None):
        self.measReports = _ensureIsList(measReports)

    def asdict(self):
        return_dict = {}
        if self.measReports[0].measFrequency:
            return_dict["rcvdPowerMeasReports"] = _toJsonDictArray(self.measReports)
        elif self.measReports[0].indoorLoss:
            return_dict["indoorLossGNSSMeasReports"] = _toJsonDictArray(self.measReports)

        return return_dict


class RcvdPowerMeasReport:
    """
    RcvdPowerMeasReport - used both for WITH and WITHOUT_GRANT configs
    Attibutes
    ---------
    measFrequency : number (required)
        Frequency of the lowest end of the measured frequency range in Hz.
    
    measBandwidth : number (required)
        Measurement bandwidth in Hz used by CBSD to perform the Received Power measurement. 
        The range bounded by measFrequency as the lower bound  and (measFrequency+ measBandwidth) as the upper bound
        expresses the frequency range used in making the measurement.
    
    measRcvdPower : number (required)
        Received Power measurement in units of dBm.  
        The range of this parameter is -100dBm .. -25dBm. 
        The Received Power is measured over the frequency range from measFrequency as the lower bound to (
        measFrequency + measBandwidth) as the upper bound.
    """

    def __init__(self, measFrequency, measBandwidth, measRcvdPower):
        self.measFrequency = measFrequency  # R
        self.measBandwidth = measBandwidth  # R
        self.measRcvdPower = measRcvdPower  # R

    def asdict(self):
        return_dict = {}
        if self.measFrequency:
            return_dict["measFrequency"] = self.measFrequency
        if self.measBandwidth:
            return_dict["measBandwidth"] = self.measBandwidth
        if self.measRcvdPower:
            return_dict["measRcvdPower"] = self.measRcvdPower
        return return_dict


class IndoorLossGNSSMeasReport:
    """
    IndoorLossGNSSMeasReport - Reports of indoor loss associated with direction (Azimuth and Elevation)
    
    Attributes
    ----------
    indoorLoss : number (required)
        A number representingindoorloss measurement in units of dB. 
        This number is a float ranging from 0 dB to 70 dB
    azimuthAngleWithGNSS : number (required)
        A number representing azimuth angle associating the direction of each indoor loss measurement in degrees. 
        This number is an integer ranging from 0 to 359degrees(0 degrees is true north, 90 degrees is East)
    elevationAngleWithGNSS : number (required)
        A number representing elevation angle associating the direction of each indoor loss measurement in degrees. 
        This number is an integer ranging from 0 to 90 degrees, (0 degrees at horizon, 90 degrees at zenith)
    technologyType : string (required)
        A string representing what technology type is being used to measure indoor loss.
        Allowed types can be found pg. 10 of WINNF-SSC-0002.pdf V8.0
    """

    def __init__(self, indoorLoss, azimuthAngleWithGNSS, elevationAngleWithGNSS, technologyType):
        self.indoorLoss = indoorLoss
        self.azimuthAngleWithGNSS = azimuthAngleWithGNSS
        self.elevationAngleWithGNSS = elevationAngleWithGNSS
        self.technologyType = technologyType

    def asdict(self):
        return_dict = {}
        if self.indoorLoss:
            return_dict["indoorLoss"] = self.indoorLoss
        if self.azimuthAngleWithGNSS:
            return_dict["azimuthAngleWithGNSS"] = self.azimuthAngleWithGNSS
        if self.elevationAngleWithGNSS:
            return_dict["elevationAngleWithGNSS"] = self.elevationAngleWithGNSS
        if self.technologyType:
            return_dict["technologyType"] = self.technologyType
        return return_dict


class SpectrumInquiryResponse:
    """
    SpectrumInquiryResponse - Array of SpectrumInquiryResponse objects. 
    Each SpectrumInquiryResponse object represents a spectrum inquiry response to a spectrum inquiry request of a CBSD.
    Attributes
    ----------
    cbsdId : string (conditional)
        This parameter is included if and only if the cbsdId parameter in the SpectrumInquiryRequest object contains a
        valid CBSD identity.If included, the SAS shall set this parameterto the value of the cbsdIdparameter in the
        corresponding SpectrumInquiryRequestobject.
    availableChannel : array of object AvailableChannel (conditional)
        This parameter is an array of zero or more data objects, AvailableChannel, which describes a channel that is
        available for the CBSD, see Table 21. Included: If and only if the Spectrum Inquiry is successful.
    response : object Response (required)
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason. See Table 14: ResponseObject Definition
    """

    def __init__(self, cbsdId=None, availableChannel=None, response=Response(102)):
        self.cbsdId = cbsdId  # C
        self.availableChannel: List[AvailableChannel] = _ensureIsList(availableChannel) if availableChannel else []
        self.response: Response = response if response else Response(102)

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.availableChannel:
            return_dict["availableChannel"] = _toJsonDictArray(self.availableChannel)
        if self.response:
            return_dict["response"] = self.response.asdict()
        return return_dict


class AvailableChannel:
    """
    AvailableChannel - 
    Attributes
    ----------
    frequencyRange : object FrequencyRange (required)
        This parameter is the frequency range of the available channel, see Table 17.
    
    channelType : string (required)
        "PAL": the frequency range is a PAL channel. "GAA": the frequency range is for GAA use.
    ruleApplied : string (required)
        The regulatory rule used to generate this response, e.g., "FCC_PART_96".
    maxEirp : number (optional)
        Maximum EIRP likely to be permitted for a Grant on this frequencyRange, given the CBSD registration
        parameters, including location, antenna orientation and antenna pattern. The maximum EIRP is in the units of
        dBm/MHzand is an integer or a floating point value between -137 and +37 (dBm/MHz) inclusive.
    grantRequest : array of object GrantRequest (required)
        Array of GrantRequest objects. Each    GrantRequest object represents a Grant request of a CBSD.
    """

    def __init__(self, frequencyRange, channelType, ruleApplied, maxEirp=None, grantRequest=None):
        self.frequencyRange = frequencyRange
        self.channelType = channelType
        self.ruleApplied = ruleApplied
        self.maxEirp = maxEirp
        self.grantRequest: List[GrantRequest] = grantRequest if grantRequest else []

    def asdict(self):
        return_dict = {}
        if self.frequencyRange:
            return_dict["frequencyRange"] = self.frequencyRange.asdict()
        if self.channelType:
            return_dict["channelType"] = self.channelType
        if self.ruleApplied:
            return_dict["ruleApplied"] = self.ruleApplied
        if self.maxEirp:
            return_dict["maxEirp"] = self.maxEirp
        return_dict["grantRequest"] = self.grantRequest

        return return_dict


class GrantRequest:
    """
    GrantRequest - Array of GrantRequest objects. Each GrantRequest object represents a Grant request of a CBSD.
    Attributes
    ----------
    cbsdId : string (required)
        The CBSD shall set this parameter to the value of its CBSD identity.
    operationParam : object OperationParam (required)
        This data object includes operation parameters of the requested Grant.
    measReport : object MeasReport (conditional)
        The CBSD uses this parameter to report measurements to the SAS. 
        The format of the MeasReport object is provided in [n.21].
        Referto section 8 and [n.21] for inclusion rules
    vtGrantParams : object VTGrantParams
        Object used for research data collection.
        This is not a WinnForum specified data type.
    
    """

    def __init__(self, cbsdId, operationParam, measReport=None, vtGrantParams=None):
        self.cbsdId = cbsdId  # R
        self.operationParam = operationParam  # R
        self.measReport: MeasReport = measReport  # C
        self.vtGrantParams = vtGrantParams  # O

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.operationParam:
            return_dict["operationParam"] = self.operationParam.asdict()
        if self.measReport:
            return_dict["measReport"] = self.measReport.asdict()
        if self.vtGrantParams:
            return_dict["vtGrantParams"] = self.vtGrantParams.asdict()
        return return_dict


class OperationParam:
    """
    OperationParam -
    Attributes
    ----------
    maxEirp : number (required)
        Maximum EIRP permitted by the Grant. 
        The maximum EIRP is in the units of dBm/MHz and is an integer or a floating point value between -137 and +37 (
        dBm/MHz) inclusive.
        The value of maxEirp represents the average (RMS) EIRP that would be measured per the procedure defined in FCC
        §96.41(e)(3)and shall not exceed eirpCapability-10.
    operationFrequencyRange : object FrequencyRange (required)
        This parameter is frequency range of a contiguous segment.
    """

    def __init__(self, maxEirp, operationFrequencyRange):
        self.maxEirp = maxEirp  # R
        self.operationFrequencyRange: FrequencyRange = operationFrequencyRange  # R

    def asdict(self):
        return_dict = {}
        if self.maxEirp:
            return_dict["maxEirp"] = self.maxEirp
        if self.operationFrequencyRange:
            return_dict["operationFrequencyRange"] = self.operationFrequencyRange.asdict()
        return return_dict


class VTGrantParams:
    """
    Parameters for extended grant request data.
    For VT Research purposes only.
    """

    def __init__(self, minFrequency, maxFrequency, preferredFrequency, frequencyAbsolute, minBandwidth,
                 maxBandwidth, preferredBandwidth, startTime, endTime, approximateByteSize, dataType, powerLevel,
                 location, mobility, maxVelocity):
        self.minFrequency = minFrequency
        self.maxFrequency = maxFrequency
        self.preferredFrequency = preferredFrequency
        self.frequencyAbsolute = frequencyAbsolute
        self.minBandwidth = minBandwidth
        self.maxBandwidth = maxBandwidth
        self.preferredBandwidth = preferredBandwidth
        self.startTime = startTime
        self.endTime = endTime
        self.approximateByteSize = approximateByteSize
        self.dataType = dataType
        self.powerLevel = powerLevel
        self.location = location
        self.mobility = mobility
        self.maxVelocity = maxVelocity

    def asdict(self):
        return_dict = {}
        if self.minFrequency:
            return_dict["minFrequency"] = self.minFrequency
        if self.maxFrequency:
            return_dict["maxFrequency"] = self.maxFrequency
        if self.preferredFrequency:
            return_dict["preferredFrequency"] = self.preferredFrequency
        if self.frequencyAbsolute:
            return_dict["frequencyAbsolute"] = self.frequencyAbsolute
        if self.minBandwidth:
            return_dict["minBandwidth"] = self.minBandwidth
        if self.maxBandwidth:
            return_dict["maxBandwidth"] = self.maxBandwidth
        if self.preferredBandwidth:
            return_dict["preferredBandwidth"] = self.preferredBandwidth
        if self.startTime:
            return_dict["startTime"] = self.startTime
        if self.endTime:
            return_dict["endTime"] = self.endTime
        if self.approximateByteSize:
            return_dict["approximateByteSize"] = self.approximateByteSize
        if self.dataType:
            return_dict["dataType"] = self.dataType
        if self.powerLevel:
            return_dict["powerLevel"] = self.powerLevel
        if self.location:
            return_dict["location"] = self.location
        if self.mobility:
            return_dict["mobility"] = self.mobility
        if self.maxVelocity:
            return_dict["maxVelocity"] = self.maxVelocity
        return return_dict


class GrantResponse:
    """
    GrantResponse - Array of GrantResponseobjects.
        Each GrantResponseobject represents a Grantresponseto a Grant request of a CBSD
    
    Attributes
    ----------
    cbsdId : string (conditinoal)
        his parameter is includedif and only if the cbsdId parameter in the GrantRequest object contains a valid CBSD
        identity.If included, the SAS shall set this parameterto the value of the cbsdIdparameter in the corresponding
        GrantRequestobject.
    grantId : string (contitional)
        An ID provided by the SAS for this Grant. Included: If and only if the Grant request is approved by the SAS.
        The CBSD shall set the Grant identity for this Grant to the value received in this parameter.
    grantExpireTime : string (conditional)
        The grantExpireTime indicates the time when the Grant associated with the grantId expires. 
        This parameter is UTC time expressed in the format, YYYY-MM-DDThh:mm:ssZ as defined by [n.7].
        This parameter shall be included if and only if the responseCodeparameter indicates SUCCESS.
        If the channelTypeparameter is included in this object and the value is set to "PAL",
        the grantExpireTimeparameter shall be set to the value that does not extend beyond the licenseExpiration of
        the corresponding PAL recorded in the PAL Database [n.23].
    heartbeatInterval : number (conditional)
        This parameter is a positive integer and indicates the maximum time interval in units of seconds between two
        consecutive heartbeat requests that the CBSD should attempt to meet.
        This parameter shall be included if the responseCode parameter indicates SUCCESS.
    measReportConfig : array of string (optional)
        The SAS uses this parameter to configure CBSD measurement reporting. 
        The measurement report requested by the SAS shall be consistent with the CBSD measurement capabilities
        reportedduring the registration request. The CBSD shall report the measurementslisted in this array.
        The permitted enumerations arespecified in [n.21]
    operationParam : object OperationParam (optional)
        If the Grant request is disapproved, using this object the SAS can optionally provide a new set of operation
        parameters to the CBSDfor use in a new Grant request.
    channelType : string (conditional)
        This parameter is included if and only if the responseCodeparameter indicates SUCCESS, i.e., the Grant request
        was successful."PAL": the frequency range is a PAL channel."GAA": the frequency range is for GAA use.
    response : object Response (required)
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason.  See Table 14.
    """

    def __init__(
            self, cbsdId=None, grantId=None, grantExpireTime=None, heartbeatInterval=None, measReportConfig=None,
            operationParam=None, channelType=None, response=Response(102)
    ):
        self.cbsdId = cbsdId  # C
        self.grantId = grantId  # C
        self.grantExpireTime = grantExpireTime  # C
        self.heartbeatInterval = heartbeatInterval  # C
        self.measReportConfig = _ensureIsList(measReportConfig)  # O
        self.operationParam = operationParam  # O
        self.channelType = channelType  # C
        self.response = response if response else Response(102)

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.grantId:
            return_dict["grantId"] = self.grantId
        if self.grantExpireTime:
            return_dict["grantExpireTime"] = self.grantExpireTime
        if self.heartbeatInterval:
            return_dict["heartbeatInterval"] = self.heartbeatInterval
        if self.measReportConfig[0]:
            return_dict["measReportConfig"] = self.measReportConfig
        if self.operationParam:
            return_dict["operationParam"] = self.operationParam.asdict()
        if self.channelType:
            return_dict["channelType"] = self.channelType
        if self.response:
            return_dict["response"] = self.response.asdict()
        return return_dict


class HeartbeatRequest:
    """
    HeartbeatRequest - Array of HeartbeatRequest objects.
        Each HeartbeatRequest object represents a heartbeat request of a CBSD.
    
    Attributes
    ----------
    cbsdId : string (required)
        The CBSD shall set this parameter to the value ofitsCBSD identity
    grantId : string (required)
        The CBSD shall set this parameter to the value ofthe Grant identity of this Grant.
    grantRenew : boolean (optional)
        If set to True, the CBSD asks for renewal of the current Grant. SAS shall include a grantExpireTimeparameter
        in the following HeartbeatResponseobject.
    operationState : string (required)
        This parameter contains the CBSD operation state ("AUTHORIZED" or "GRANTED").
    measReport : object MeasReport (conditional)
        The CBSD uses this parameter to report measurements to the SAS. The format of the MeasReport object is
        provided in [n.21].
        Refer to section 8 and [n.21] for inclusion rules.
    """

    def __init__(self, cbsdId, grantId, grantRenew=None, operationState="ERR: Nothing Provided",
                 measReport=None):
        self.cbsdId = cbsdId  # R
        self.grantId = grantId  # R
        self.grantRenew = grantRenew  # O
        self.operationState = operationState  # R
        self.measReport = measReport  # C

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.grantId:
            return_dict["grantId"] = self.grantId
        if self.grantRenew:
            return_dict["grantRenew"] = self.grantRenew
        if self.operationState:
            return_dict["operationState"] = self.operationState
        if self.measReport:
            return_dict["measReport"] = self.measReport.asdict()
        return return_dict


class HeartbeatResponse:
    """
    HeartbeatResponseObject - Array of HeartbeatResponseobjects. Each HeartbeatResponse object represents a heartbeat
    response of a CBSD.
    
    Attributes
    ----------
    cbsdId : string (conditional)
        This parameter is included if and only if the cbsdId parameter in the HeartbeatRequest object contains a valid
        CBSD identity.
        If included, the SAS shall set this parameterto the value of the cbsdIdparameter in the corresponding
        HeartbeatRequestobject.
    grantId : string (conditional)
        This parameter is included if and only if the grantId parameter in the HeartbeatRequest object contains a
        valid Grant identity.
        If included, the SAS shall set this parameterto the value of the grantIdparameter in the corresponding
        HeartbeatRequestobject.
    transmitExpireTime : string (required)
        The CBSD shall cease transmission using the SAS authorized radio resource within 60 seconds after the value of
        the transmitExpireTimeparameter expires, in accordance with part 96.39(c)(2) (ref. [n.8]).
        The transmitExpireTimeis UTC time expressed in the format, YYYY-MM-DDThh:mm:ssZ as defined by [n.7].The
        transmitExpireTimevalue shall be no later thanthe grantExpireTime
    grantExpireTime : string (conditional)
        Required if the responseCode parameter indicates SUCCESS or SUSPENDED_GRANT and the grantRenew parameter was
        included and set to True in the corresponding HeartbeatRequestobject.
        This parameter may be included at other times by SAS choice.When included, if the channelTypeof this Grantis
        "PAL", thisparameter shall be set to the value that does not extend beyond the licenseExpirationof the
        corresponding PAL recorded in the PAL Database [n.23].
        
    heartbeatInterval : number (optional)
        This parameter is a positive integer and indicates the maximum time interval in units of seconds between two
        consecutive heartbeat requeststhat the CBSD should attempt to meet.
        This parameter isincluded when the SAS wants tochange the heartbeat interval.
    operationParam : object OperationParam (optional)
        If heartbeat request is disapproved or the SAS intends to change the CBSD operation parameters, the SAS can
        provide a new set of operation parameters to the CBSD using this objectas arecommendation to request a new
        Grant
    measReportConfig : array of string (optional)
        The SAS uses this parameter to configure CBSD measurement reporting. 
        The measurement report requested by the SAS shall be consistent with the CBSD measurement capabilities
        reportedduring the registration request.
        The CBSD shall report the measurement listed in this array. 
        The permitted enumerations are specified in [n.21].
    response : object Response (required)
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason.  See Table 14.
    """

    def __init__(self, cbsdId=None, grantId=None, transmitExpireTime="-1", grantExpireTime=None,
                 heartbeatInterval=None, operationParam=None, measReportConfig=None, response=Response(102)):
        self.cbsdId = cbsdId  # C
        self.grantId = grantId  # C
        self.transmitExpireTime = transmitExpireTime  # R
        self.grantExpireTime = grantExpireTime  # C
        self.heartbeatInterval = heartbeatInterval  # O
        self.operationParam = operationParam  # O
        self.measReportConfig = _ensureIsList(measReportConfig)  # O
        self.response = response if response else Response(102)

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.grantId:
            return_dict["grantId"] = self.grantId
        if self.transmitExpireTime:
            return_dict["transmitExpireTime"] = self.transmitExpireTime
        if self.grantExpireTime:
            return_dict["grantExpireTime"] = self.grantExpireTime
        if self.heartbeatInterval:
            return_dict["heartbeatInterval"] = self.heartbeatInterval
        if self.operationParam:
            return_dict["operationParam"] = self.operationParam.asdict()
        if self.measReportConfig[0]:
            return_dict["measReportConfig"] = self.measReportConfig
        if self.response:
            return_dict["response"] = self.response.asdict()
        return return_dict


class RelinquishmentRequest:
    """
    RelinquishmentRequest - Array of RelinquishmentRequest objects.
        Each RelinquishmentRequest object Represents a relinquishment request of a CBSD.
    
    Attributes
    ----------
    cbsdId : string (required)
        The CBSD shall set this parameter to the value of its CBSD identity.
    grantId : string (required)
        The CBSD shall set this parameter to the value of the Grant identity of this Grant.
    """

    def __init__(self, cbsdId, grantId):
        self.cbsdId = cbsdId  # R
        self.grantId = grantId  # R

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.grantId:
            return_dict["grantId"] = self.grantId
        return return_dict


class RelinquishmentResponse:
    """
    RelinquishmentResponse - Array of RelinquishmentResponse objects. 
        Each RelinquishmentResponseobject represents a relinquishment response to a relinquishment request of a CBSD.
    
    Attributes
    ----------
    cbsdId : string (conditional)
        This parameter is included if and only if the cbsdId parameter in the RelinquishmentRequest object contains a
        valid CBSD identity.  If included, the SAS shall set this parameter to the value of the cbsdId parameter in
        the corresponding RelinquishmentRequest object.
    grantId : string (conditional)
        This parameter is included if and only if the grantId parameter in the RelinquishmentRequest object contains a
        valid Grant identity.  If included, the SAS shall set this parameter to the value of the grantId parameter in
        the corresponding RelinquishmentRequest object.
    response : object Response (required)
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason. See Table 14: ResponseObject Definition.
    """

    def __init__(self, cbsdId=None, grantId=None, response=Response(102)):
        self.cbsdId = cbsdId  # C
        self.grantId = grantId  # C
        self.response = response

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.grantId:
            return_dict["grantId"] = self.grantId
        if self.response:
            return_dict["response"] = self.response.asdict()
        return return_dict


class DeregistrationRequest:
    """
    DeregistrationRequest - Array of DeregistrationRequest data objects. 
        Each DeregistrationRequest data object represents a deregistrationrequest of a CBSD.
    
    Attributes
    ----------
    cbsdId : string (required)
        The CBSD shall set this parameter to the value of its CBSD identity.
    """

    def __init__(self, cbsdId):
        self.cbsdId = cbsdId  # R

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        return return_dict


class DeregistrationResponse:
    """
    DeregistrationResponse - Array of DeregistrationResponsedata objects.
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
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason.  See Table 14: ResponseObject Definition
    """

    def __init__(self, cbsdId=None, response=Response(102)):
        self.cbsdId = cbsdId  # C
        self.response = response  # R

    def asdict(self):
        return_dict = {}
        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.response:
            return_dict["response"] = self.response.asdict()
        return return_dict


class Grant:
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
        This parameter includes information on whether the corresponding CBSD request is approved or disapproved for a
        reason.  See Table 14: ResponseObject Definition
    """

    def __init__(self, id, cbsdId, operationParam, vtGrantParams=None, expireTime=None, heartbeatTime=None,
                 heartbeatInterval=None, response=Response(102)):
        self.id = id
        self.cbsdId = cbsdId  # R
        self.operationParam = operationParam  # R
        self.vtGrantParams = vtGrantParams  # O
        self.expireTime = expireTime
        self.heartbeatTime = heartbeatTime
        self.heartbeatInterval = heartbeatInterval
        self.response = response

    def asdict(self):
        return_dict = {"id": self.id}

        if self.cbsdId:
            return_dict["cbsdId"] = self.cbsdId
        if self.operationParam:
            return_dict["operationParam"] = self.operationParam.asdict()
        if self.vtGrantParams:
            return_dict["vtGrantParams"] = self.vtGrantParams.asdict()
        if self.expireTime:
            return_dict["expireTime"] = self.expireTime
        if self.heartbeatTime:
            return_dict["heartbeatTime"] = self.heartbeatTime
        if self.heartbeatInterval:
            return_dict["heartbeatInterval"] = self.heartbeatInterval
        return_dict["response"] = self.response

        return return_dict
