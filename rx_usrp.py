#!/usr/bin/env python3
from gnuradio import blocks
from gnuradio import fft
from gnuradio import gr
from gnuradio import uhd
from gnuradio.fft import window
import time

# Example Command to activate_rx: sas_test_server must be activate_rxning before entering this cmd
# ./sas_radio_interface.py -p 65431 -a 127.0.0.3 -d "192.168.40.105" --freq 914.5 --bandwidth 0.1 --bins 100


class rx_usrp(gr.top_block):
    """
    Class representing a USRP Receiver Flowgraph

    Attributes
    ----------
    centerFreq : double
        center frequency of the band you want to receive
    bins : int
        # of FFT bins the received data will be represented
    bandwidth : double
        bandwidth of the signal you want to receive
    deviceAddr : string 
        IP address of the USRP to use as Rx

    Methods
    ------- 
    """

    def __init__(self, deviceAddr, centerFreq, bins, sample_rate, bandwidth=0, gain=0):
        """
        Constructs Rx object

        Parameters
        ----------
        centerFreq : double
            center frequency of the band you want to receive
        bins : int
            # of FFT bins the received data will be represented
        bandwidth : double
            bandwidth of the signal you want to receive,
             only some daghterboards support this
        deviceAddr : string 
            IP address of the USRP to use as Rx

        """

        gr.top_block.__init__(self, "SAS Receiver USRP")


        ##################################################
        # Variables
        ##################################################
        self.SDR_Address = deviceAddr
        self.freq        = centerFreq
        self.bins        = bins
        self.sample_rate = sample_rate
        self.bandwidth   = bandwidth
        self.gain        = gain

        ##################################################
        # Blocks
        ##################################################
        self.RX_USRP = uhd.usrp_source(
            device_addr="addr="+deviceAddr,
            stream_args=uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        self.RX_USRP.set_samp_rate(sample_rate)
        self.RX_USRP.set_center_freq(centerFreq, 0)
        self.RX_USRP.set_gain(gain, 0) # Absolute Gain: 0 - 1
        self.RX_USRP.set_bandwidth(bandwidth, 0)
        # self.RX_USRP.set_antenna('TX/RX', 0) #TODO: RX1, RX2, or TX\RX, daughterboard dependant
        self.RX_USRP.set_time_unknown_pps(uhd.time_spec())
        self.fft_vxx_0 = fft.fft_vcc(bins, True, (window.blackmanharris(bins)), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex, bins)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(bins)
        self.blocks_nlog10_0 = blocks.nlog10_ff(20, bins, 0)
        self.blocks_probe_signal_vx_0 = blocks.probe_signal_vf(bins)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.RX_USRP, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_nlog10_0, 0))
        self.connect((self.blocks_nlog10_0, 0), (self.blocks_probe_signal_vx_0, 0))

    def set_SDR_Address(self, address):
        """
        Updates which CRTS Node to use *UNTESTED*

        Parameters
        ----------
        address : string
            desired node address
        """
        # TODO: Possibly destroy uhd.usrp_source object to... 
        #... recreate a new one with the new address?
        self.SDR_Address = address

    def get_SDR_Address(self):
        """
        Returns Address of RX Radio

        Return
        ------
        address : string
            RX node IP address
        """
        return self.SDR_Address

    def set_freq(self, freq):
        """
        Updates Center Frequency of RX

        Parameters
        ----------
        cFreq : double
            desired center frequency
        """
        self.freq = freq
        self.RX_USRP.set_center_freq(freq, 0)

    def get_freq(self):
        """
        Returns Cetner Frequencey of RX Radio

        Return
        ------
        cFreq : double
            RX center frequency
        """
        return self.freq

    def set_sample_rate(self, sample_rate):
        """
        Updates Gain of RX

        Parameters
        ----------
        sample rate : double
            desired sample rate
        """
        self.gain = sample_rate
        self.RX_USRP.set_samp_rate(sample_rate)

    def get_sample_rate(self):
        """
        Returns Sample Rate of RX Radio

        Return
        ------
        sample rate : double
            current sampling rate
        """
        return self.sample_rate

    def set_bandwidth(self, bandwidth):
        """
        Updates Bandwidth of RX

        Parameters
        ----------
        bandwidth : double
            desired bandwidth
        """
        self.bandwidth = bandwidth
        self.RX_USRP.set_bandwidth(bandwidth, 0)

    def get_bandwidth(self):
        """
        Returns Bandwidth of RX Radio

        Return
        ------
        bandwidth : double
            RX bandwidth
        """
        return self.bandwidth

    def set_gain(self, gain):
        """
        Updates Gain of RX

        Parameters
        ----------
        gain : double
            desired gain
        """
        self.gain = gain
        self.RX_USRP.set_gain(gain, 0)

    def get_gain(self):
        """
        Returns Gain of RX Radio

        Return
        ------
        gain : double
            radio rx gain
        """
        return self.gain

