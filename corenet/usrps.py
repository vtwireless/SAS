#!/usr/bin/env python3
# TX Imports------------------------------------
from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
# End TX Imports---------------------------------


# TODO: 'type' may be a reserved word
# TODO: make this 'usrp.py' and include both TX and RX flowgraphs in here

class Grant:
    """
    One node may have one Grant object.
    Source: Page 7 of https://winnf.memberclicks.net/assets/CBRS/WINNF-TS-0016.pdf

    Attributes
    ----------
    grantId : string
        grantId assigned by the SAS upon sucessful Grant request
    grantStatus : string
        One of three possile states for a Grant (IDLE, GRANTED, AUTHORIZED)
    grantExpireTime : string
        Time at which the grant is no longer valid

    Methods
    -------
    getGrantId()
        returns grantId for the Grant the node is assigned to
    setGrantId(id)
        assigns instance variable grantId to passed parameter id
    getGrantStatus()
        returns grantStatus for the Grant the node is assigned to
    setGrantStatus(status)
        assigns instance variable grantStatus to passed parameter status
    """
    def __init__(self):
        """
        Constructor for a Grant Object. Grants are created once a node registers on the SAS.
        Nodes are automatically sent to IDLE since they have yet to send a sucessfull Grant request.
        """
        self.grantId         = ""
        self.grantStatus     = "IDLE"
        self.grantExpireTime = ""
    
    def getGrantId(self):
        """
        Returns grantId for the Grant the node is assigned to

        Returns
        -------
        grantId : string
            ID of grant the Node is assigned to 
        """ 
        return self.grantId

    def setGrantId(self, id):
        """
        Assigns instance variable grantId to passed parameter id
        """
        self.grantId = id
    
    def getGrantStatus(self):
        """
        Returns grantStatus for the Grant the node is assigned to
        """
        return self.grantStatus

    def setGrantStatus(self, status):
        """
        Assigns instance variable grantStatus to passed parameter status
        """
        self.grantStatus = status

    def getGrantExpireTime(self):
        """
        Returns grantExpireTime for the Grant the node is assigned to
        """
        return self.grantExpireTime

    def setGrantExpireTime(self, expireTime):
        """
        Assigns instance variable grantExpireTime to passed parameter status
        """
        self.grantExpireTime = expireTime

class TX_Usrp(gr.top_block):
    """
    Class representing a USRP Transmitter Flowgraph

    Attributes
    ----------
    centerFreq : double
        center frequency of the band you want to transmit
    bins : int
        # of FFT bins the received data will be represented
    bandwidth : double
        bandwidth of the signal you want to create
    deviceAddr : string 
        IP address of the USRP to use as Tx

    Methods
    ------- 
    TODO: Lots to add here
    """

    def __init__(self, deviceAddr, centerFreq, gain, sampRate, signalAmp, waveform):
        """
        Constructs Tx USRP object

        Parameters
        ----------
        deviceAddr : string 
            IP address of the USRP to use as Rx
        centerFreq : double
            center frequency of the band you want to receive
        gain : double
            dB gain of transmitted signal
        sampRate : int
            # of FFT bins the received data will be represented
        signalAmp : float
            Amplitude of signal from 0 to 1
        waveform : string
            Type of waveform (SINE, SAWTOOTH, etc)         
        """

        gr.top_block.__init__(self, "SAS USRP Transmitter")

        ##################################################
        # Variables
        ##################################################
        self.SDR_Address = deviceAddr   # Required
        self.freq        = centerFreq   # Required 
        self.gain        = gain         # Required 
        self.sample_rate = sampRate     # Required
        self.signal_amp  = signalAmp    # Required
        self.waveform    = waveform     # Required


        # NOTE: If GNURadio were to change how is generates TX Usrps that are fed by a singal source...
        # ...then that code can be pasted in here to simply update to this system
        ##################################################
        # Blocks
        ##################################################
        self.interest_signal = analog.sig_source_c(self.sample_rate, self.waveform, 0, self.signal_amp, 0, 0)
        self.SDR_A = uhd.usrp_sink(
            ",".join(("addr="+self.SDR_Address, '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.SDR_A.set_center_freq(self.freq, 0)
        self.SDR_A.set_gain(self.gain, 0)
        self.SDR_A.set_antenna('TX/RX', 0) # May need to add controls to this param
        self.SDR_A.set_samp_rate(self.sample_rate)

        # This is used to coordinate changes across mulitple devices it seems like
        # It looks as though an external LO is used to get this nanosecond timing correct
        # Can look into this feature at a later time when mulitple devices are working for the SAS
        self.SDR_A.set_time_unknown_pps(uhd.time_spec()) # TODO: Learn more about this ^

        ##################################################
        # Connections
        ##################################################
        self.connect((self.interest_signal, 0), (self.SDR_A, 0))

    

    def get_SDR_Address(self):
        return self.SDR_Address

    # I do not believe that changing SDR_Address will cause any effect at this time
    def set_SDR_Address(self, SDR_Address):
        self.SDR_Address = SDR_Address

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.SDR_A.set_center_freq(self.freq, 0)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.SDR_A.set_gain(self.gain, 0)

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.SDR_A.set_samp_rate(self.sample_rate)
        self.interest_signal.set_sampling_freq(self.sample_rate)

    def get_signal_amp(self):
        return self.signal_amp

    def set_signal_amp(self, signal_amp):
        self.signal_amp = signal_amp
        self.interest_signal.set_amplitude(self.signal_amp)

    def get_waveform(self):
        return self.waveform

    def set_waveform(self, waveform):
        self.waveform = self._convert_waveform(waveform)
        
class Node:
    """
    Highest level Node class. This containts 2 flowgrahs for 1 USRP, Grant, and other node/cbsd data.

    Attributes
    ----------
    operationMode : string
        This will either be 'TX' or 'RX'. 
    tx_usrp : TX_Usrp Object
        Object associated with the TX Flowgraph
    rx_usrp : RX_Usrp Object
        Object associated with the RX Flowgraph
    grant : Grant object
        All nodes will have 1 Grant that includes all grant related data
    cbsdId : string
        ID of the node as given by the SAS upon registration

    Methods
    -------
    """

    def __init__(self, ipAddress):
        """
        Constructor for a Node object
        """

        #TODO do not duplicate with create_nodes that are inactive
        __available_radios = list(uhd.find_devices()) # Pull list of nodes available once, for use when creating usrp obj

        self.ipAddress        = ipAddress
        self.serialNum        = self._ipToSerial(ipAddress, __available_radios)
        self.model            = self._getProductOrType(ipAddress, __available_radios)
        self.operationMode    = ""
        self.tx_usrp          = ""
        self.rx_usrp          = "" 
        self.grant            = ""
        self.cbsdId           = ""
        self.measReportConfig = []
    
    def getIpAddress(self):
        return self.ipAddress

    def setIpAddress(self, ip):
        self.ipAddress = ip

    def getSerialNumber(self):
        return self.serialNum

    def setSerialNumber(self, num): 
        self.serialNum = num
    
    def getModel(self):
        return self.model
    
    def setModel(self, model):
        self.model = model

    def getOperationMode(self):
        return self.operationMode

    def setOperationMode(self, mode):
        self.operationMode = mode 

    def getTxUsrp(self):
        return self.tx_usrp

    def setTxUsrp(self, centerFreq, gain, sampRate, signalAmp, waveform):
        """
        Creates a TX USRP Flowgraph (but does not start it)
        All passed in parameters are checked for validity.
        A USRP will not be created if any parameters are not compatible with the USRP.

        TODO with Xavier

        Returns
        -------
        validParams : boolean
            True if USRP can handle the demanded parameters, False otherwise
        """
        if((centerFreq > 0) and (gain >= 0) and (sampRate > 0) and (signalAmp >= 0) and (self._convert_waveform(waveform))):
            self.tx_usrp = TX_Usrp(self.ipAddress, centerFreq, gain, sampRate, signalAmp, self._convert_waveform(waveform))
            return True
        else:
            return False
        
    def getRxUsrp(self):
        return self.rx_usrp

    def setRxUsrp(self, usrp):# TODO: Determine parameters for this
        self.rx_usrp = usrp
    
    def getGrant(self):
        return self.grant

    def setGrant(self, grant):
        self.grant = grant

    def getCbsdId(self):
        return self.cbsdId 

    def setCbsdId(self, id):
        self.cbsdId = id
    
    def getMeasReportConfig(self):
        return self.measReportConfig
    
    def setMeasReportConfig(self, config):
        self.measReportConfig = config

# Helper Functions------------------------------
    def _ipToSerial(self, ip, __available_radios):
        """
        Takes USRP IP Address and returns its serial number.
        If no USRP is found with the given serial number, then return 'N/A'.

        Parameter
        ---------
        ip : string
            IP address of USRP to find serial number
        """
        for node in __available_radios:
            if(ip == node['addr']):
                return node['serial']
        return "N/A" # If no serial matches the IP Address provided

    def _getProductOrType(self, ip, __available_radios):
        """
        Using USRP IP Address, find the USRP product/type (e.g. X310 or usrp2).

        Returns
        -------
        usrpType : string
            USRP product or type. If no match, returns 'N/A'
        """
        for node in __available_radios:
            try:
                if(ip == node['addr']):
                    try:
                        return node['product']
                    except RuntimeError:
                        try:
                            return node['type']
                        except RuntimeError:
                            pass
            except:
                pass
        return "N/A"
    
    def _convert_waveform(self, waveform):
        """
        Converts User Input Wavefore into GNU Radio Waveform
        
        Parameters
        ----------
        waveform : string
            User friendly string representing waveform type

        Return
        ------
            GNU Radio waveform library value. Defaults to Sine Wave. 
        """
        if(waveform == "CONSTANT"):
            return analog.GR_CONST_WAVE
        elif(waveform == "COSINE"):
            return analog.GR_COS_WAVE
        elif(waveform == "SQUARE"):
            return analog.GR_SQR_WAVE
        elif(waveform == "TRIANGLE"):
            return analog.GR_TRI_WAVE
        elif(waveform == "SAWTOOTH"):
            return analog.GR_SAW_WAVE
        elif(waveform == "SINE"):
            return analog.GR_SIN_WAVE
        else:
            return None
# End Helper Functions--------------------------
