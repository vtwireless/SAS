#!/usr/bin/env python3
from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd

# TODO: 'type' may be a reserved word
# TODO: make this 'usrp.py' and include both TX and RX flowgraphs in here

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
    """

    def __init__(self, deviceAddr, centerFreq, gain, sampRate, signalAmp, waveform, cbsdId=None, mode=None, data_type=None, grantId=None):
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
        self.SDR_Address = deviceAddr
        self.freq        = centerFreq
        self.gain        = gain
        self.sample_rate = sampRate
        self.signal_amp  = signalAmp
        self.waveform    = self._convert_waveform(waveform)
        self.cbsdId      = cbsdId
        self.mode        = mode   # Either build a TX or RX for this parameter
        self.data_type   = "type" # TODO @Joseph is this data type? Video vs Text?
        self.grantId     = grantId

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

    def set_GrantId(self, grantId):
        self.grantId = grantId

    def get_GrantId(self):
        return self.grantId
 
    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def set_CbsdId(self, cbsdId):
        self.cbsdId = cbsdId

    def get_CbsdId(self):
        return self.cbsdId

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