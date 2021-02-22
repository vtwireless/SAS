#!/usr/bin/env python3

# Imports------------------------------------
from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
# End Imports---------------------------------


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
    heartbeatInterval : string (integer)
        Maximum number of seconds allowed between Heartbeats
    channelType : string
        "PAL" or "GAA" channel descriptor
        
    Methods
    -------
    getGrantId()
        returns grantId for the Grant the node is assigned to
    setGrantId(id)
        assigns grantId to passed parameter id
    getGrantStatus()
        returns grantStatus for the Grant the node is assigned to
    setGrantStatus(status)
        assigns grantStatus to passed parameter status
    getGrantExpireTime
        returns grantExpireTime for the Grant the node is assigned to
    setGrantExpireTime(expireTime)
        assigns grantExpireTime to passed parameter expireTime
    """
    def __init__(self):
        """
        Constructor for a Grant Object. Grants are created once a node registers on the SAS.
        Nodes are automatically sent to IDLE since they have yet to send a sucessfull Grant request.
        """
        self.grantId           = ""
        self.grantStatus       = "IDLE"
        self.grantExpireTime   = ""
        self.heartbeatInterval = "" 
        self.channelType       = ""
    
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
        Assigns grantId to passed parameter id
        """
        self.grantId = id
    
    def getGrantStatus(self):
        """
        Returns grantStatus for the Grant the node is assigned to
        """
        return self.grantStatus

    def setGrantStatus(self, status):
        """
        Assigns grantStatus to passed parameter status
        """
        self.grantStatus = status

    def getGrantExpireTime(self):
        """
        Returns grantExpireTime for the Grant the node is assigned to
        """
        return self.grantExpireTime

    def setGrantExpireTime(self, expireTime):
        """
        Assigns grantExpireTime to passed parameter status
        """
        self.grantExpireTime = expireTime
    
    def getHeartbeatInterval(self):
        """
        Returns heartbeatInterval for the Grant the node is assigned to
        """
        return self.heartbeatInterval
    
    def setHeartbeatInterval(self, hbInt):
        """
        Assigns heartbeatInterval to passed parameter status
        """
        self.heartbeatInterval = hbInt

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

class TXRX_USRP(gr.top_block):
    """
    Class Representing a USRP TX & RX Flowgraph.

    This flowgraph works for any USRPs that have multiple channels/radios that support simultaneous TX and RX. 
    The TX will transmit a constant noise with the given params.
    
    Attributes
    ----------
    device_addr : string
        IP Address of USRP. E.g. "192.168.40.110"
    tx_fc : float
    tx_bw : float
    tx_src_amp : float
    tx_gain : float
    rx_fc : float
    rx_bw : float
    rx_gain : float
    rx_bins : float

    """

    def __init__(self, device_addr, tx_fc, tx_bw, tx_gain, tx_src_amp, rx_fc, rx_bw, rx_gain, rx_bins):
        gr.top_block.__init__(self)

        ##################################################
        # Variables
        ##################################################
        self.device_addr = device_addr
        self.tx_fc = tx_fc
        self.tx_bw = tx_bw
        self.tx_gain = tx_gain
        self.tx_src_amp = tx_src_amp 
        self.rx_fc = rx_fc
        self.rx_bw = rx_bw
        self.rx_gain = rx_gain
        self.rx_bins = rx_bins

        ##################################################
        # Blocks
        ##################################################

        # Create TX Portion
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join((device_addr, "A:")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_center_freq(tx_fc, 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_bandwidth(tx_bw, 0)
        self.uhd_usrp_sink_0.set_clock_rate(200e6, uhd.ALL_MBOARDS)
        self.uhd_usrp_sink_0.set_samp_rate(tx_bw)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec())
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_UNIFORM, tx_src_amp, 0)

        # Create RX Portion
        self.uhd_usrp_source_1 = uhd.usrp_source(
            ",".join(("addr="+device_addr, "B:")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_1.set_center_freq(rx_fc, 0)
        self.uhd_usrp_source_1.set_gain(rx_gain, 0)
        self.uhd_usrp_source_1.set_antenna('RX2', 0)
        self.uhd_usrp_source_1.set_bandwidth(rx_bw, 0)
        self.uhd_usrp_source_1.set_samp_rate(rx_bw)
        self.uhd_usrp_source_1.set_time_unknown_pps(uhd.time_spec())
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(rx_bins)
        self.fft_vxx_0 = fft.fft_vcc(rx_bins, True, window.blackmanharris(rx_bins), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, rx_bins)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, rx_bins, 0)
        self.rx_probe = blocks.probe_signal_vf(rx_bins)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.rx_probe, 0))


    def get_device_addr(self):
        return self.device_addr

    def set_device_addr(self, device_addr):
        self.device_addr = device_addr

    def get_tx_fc(self):
        return self.tx_fc

    def set_tx_fc(self, fc):
        self.tx_fc = fc
        self.uhd_usrp_sink_0.set_center_freq(self.fc, 0)

    def get_tx_bw(self):
        return self.bw

    def set_tx_bw(self, tx_bw):
        self.tx_bw = tx_bw
        self.uhd_usrp_sink_0.set_samp_rate(self.tx_bw)
        self.uhd_usrp_sink_0.set_bandwidth(self.tx_bw, 0)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, gain):
        self.tx_gain = gain
        self.uhd_usrp_sink_0.set_gain(self.gain, 0)

    def get_tx_src_amp(self):
        return self.tx_src_amp

    def set_tx_src_amp(self, src_amp):
        self.src_amp = src_amp
        self.analog_noise_source_x_0.set_amplitude(self.src_amp)

    def get_rx_fc(self):
        return self.rx_fc

    def set_rx_fc(self, fc):
        self.rx_fc = fc
        self.uhd_usrp_source_1.set_center_freq(self.fc, 0)

    def get_rx_bw(self):
        return self.rx_bw

    def set_rx_bw(self, rx_bw):
        self.rx_bw = rx_bw
        self.uhd_usrp_source_1.set_samp_rate(self.rx_bw)
        self.uhd_usrp_source_1.set_bandwidth(self.rx_bw, 0)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_1.set_gain(self.rx_gain, 0)

    def get_rx_bins(self):
        return self.rx_bins

    def set_rx_bins(self, bins):
        self.rx_bins = bins

    def getRxProbeList(self):
        """
        Grabs probe block data from flowgraph.

        Returns
        -------
        probe_data : list of floats
            List of `bins` length with spectrum data. 
        """
        return list(self.rx_probe.level())

class Node:
    """
    Highest level Node class. This containts 3 possible flowgraphs for 1 USRP, Grant, and other node/cbsd data.

    Attributes
    ----------
    operationMode : string
        This will be 'TX', 'RX', or 'TXRX'
    tx_usrp : TX_Usrp Object
        Object associated with the TX Flowgraph
    rx_usrp : RX_Usrp Object
        Object associated with the RX Flowgraph
    txrx_usrp : TXRX_USRP Object
        Object associated with TX/RX Flowgraph
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
        self.operationMode    = None
        self.usrp             = None
        self.grant            = Grant()
        self.cbsdId           = None
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

    def createTxUsrp(self, centerFreq, gain, bandwidth, signalAmp, waveform):
        """
        Creates a TX USRP Flowgraph (but does not start it)
        All passed in parameters are checked for validity.
        A USRP will not be created if any parameters are not compatible with the USRP.

        Returns
        -------
        validParams : boolean
            True if USRP can handle the demanded parameters, False otherwise
        """
        if((centerFreq > 0) and (gain >= 0) and (bandwidth > 0) and (signalAmp >= 0) and (self._convert_waveform(waveform))):
            self.usrp = TX_Usrp(self.ipAddress, centerFreq, gain, bandwidth, signalAmp, self._convert_waveform(waveform))
        else:
            return None
        
    def createRxUsrp(self, centerFreq, gain, bandwidth):# TODO: Determine parameters for this
        self.usrp = None
    
    def createTxRxUsrp(self, tx_fc, tx_bw, tx_src_amp, tx_gain, rx_fc, rx_bw, rx_gain, rx_bins=1024):
        """
        Creates a TX/RX Node with given TX & RX parameters
        """
        if(tx_gain > 31.5):
            print("TX Gain of '" + tx_gain + "' exceeds limit of 31.5. Setting TX Gain to 31.5")
            tx_gain = 31.5
        elif(tx_gain < 0):
            print("TX Gain of '" + tx_gain + "' is below minimum of 0. Setting TX Gain to 0")
            tx_gain = 0
        if(tx_src_amp > 1):
            print("TX Signal Source Amplitude of '" + tx_src_amp + "' exceeds limit of 1. Setting TX Signal Source Amplitude to 1")
            tx_src_amp = 1
        elif(tx_src_amp < 0):
            print("TX Signal Source Amplitude of '" + tx_src_amp + "' is below minimum of 0. Setting TX Signal Source Amplitude to 0 (OFF)")
            tx_src_amp = 0 # TX OFF

        self.usrp = TXRX_USRP(self.ipAddress, tx_fc, tx_bw, tx_gain, tx_src_amp, rx_fc, rx_bw, rx_gain, rx_bins)

    def getUsrp(self):
        """
        Returns
        -------
        usrp : USRP/Flowgraph Object Object
            USRP/Flowgraph Object the Node represents (May be TX, RX, or TXRX USRP)
        """
        return self.usrp

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

    def turnOffTx(self):
        """
        """
        if(self.operationMode == 'TX'):
            self.tx_usrp.set_signal_amp(0)

    def updateRxParams(self, fc=None, bw=None, gain=None):
        if(self.operationMode == "TXRX"):
            if(fc):
                self.txrx_usrp.set_rx_fc(fc)
            if(bw):
                self.txrx_usrp.set_rx_bw(bw)
            if(gain):
                self.txrx_usrp.set_rx_gain(gain)
        elif(self.operationMode == "RX"):
            if(fc):
                self.rx_usrp.set_rx_fc(fc)
            if(bw):
                self.rx_usrp.set_rx_bw(bw)
            if(gain):
                self.rx_usrp.set_rx_gain(gain)   
        else:
            print("Invalid Node for setRxParams command")       

    def getSpectrumData(self):
        """
        Uses the probe block to pull spectrum data
        """
        if(self.operationMode == "TXRX" or self.operationMode == "RX"):
            return self.usrp.getRxProbeList()
        else:
            print("Invalid function call to getSpectrumData: unsupported current operationMode '" + str(self.operationMode) + "'.")
            return None

    def printInfo(self):
        """
        This function will neatly print all Node information to the terminal
        """
        print("node data")

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
