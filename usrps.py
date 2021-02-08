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

def _ipToSerial(ip):
    """
    Takes USRP IP Address and returns its serial number
    """
    for node in list(uhd.find_devices()):
        if(ip == node['addr']):
            return node['serial']
    return "" # TODO: What happends when a serial isnt provided or found?


class Grant:
    """
    One node may have one grant object

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
    def __init__(self, grantId, grantExpireTime):
        """
        Constructor for a Grant Object

        Parameters
        ----------
        grantId : string
            grantId assigned by the SAS upon sucessful Grant request
        grantStatus : string
            One of three possile states for a Grant (IDLE, GRANTED, AUTHORIZED)
        """
        self.grantId = grantId
        self.grantStatus = "GRANTED"
        self.grantExpireTime = grantExpireTime
    
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




class tx_usrp(gr.top_block):
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

    def __init__(self, deviceAddr, centerFreq, gain, sampRate, signalAmp, waveform, cbsdId=None, mode=None, data_type=None):
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
        cbsdId : string
            ID given to node (SAS Functionality)
        mode : string
            TX or RX (SAS Functionality)
        type : string
            Not entirly sure yet...
            
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
        self.waveform    = self._convert_waveform(waveform)# Required
        self.serialNum   = _ipToSerial(deviceAddr)
        # self.model       = None # Should be able to use UHD for this also
        self.mode        = mode   # Either build a TX or RX for this parameter
        self.data_type   = "type" # TODO @Joseph is this data type? Video vs Text?
        #TODO: Pull it's own serial# and model# from UHD once the IP is passed in 

        if(mode == "TX"):
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
            self.SDR_A.set_time_unknown_pps(uhd.time_spec()) # Need to learn more about this ^


            ##################################################
            # Connections
            ##################################################
            self.connect((self.interest_signal, 0), (self.SDR_A, 0))
        elif(mode == "RX"):
            pass
        else:
            print("'" + mode + "' is an invalid mode.. (usrps.py line 107)")
            #exit?

    
    def get_serialNumber(self):
        return self.serialNum
    
    def set_serialNumber(self, val):
        self.serialNum = val

    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode

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
        

    def __convert_waveform(self, waveform):
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
        if waveform == "CONSTANT":
            return analog.GR_CONST_WAVE
        elif waveform == "COSINE":
            return analog.GR_COS_WAVE
        elif waveform == "SQUARE":
            return analog.GR_SQR_WAVE
        elif waveform == "TRIANGLE":
            return analog.GR_TRI_WAVE
        elif waveform == "SAWTOOTH":
            return analog.GR_SAW_WAVE
        else:
            return analog.GR_SIN_WAVE

class Node:
    """
    Highest level Node class. This containts a USRP, Grant, and other node/cbsd data
    """

    def __init__(self):
        """
        Constructor for a Node object
        """
        self.usrp = None
        self.grant = None
        self.cbsdId = None
    
    def getUsrp(self):
        return self.usrp
    def setUsrp(self, usrp):
        self.usrp = usrp
    
    def getGrant(self):
        return self.grant
    def setGrant(self, grant):
        self.grant = grant

    def getCbsdId(self):
        return self.cbsdId 
    def setCbsdId(self, id):
        self.cbsdId = id