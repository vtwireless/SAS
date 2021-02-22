#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Full-Duplex TX and RX USRP
# Author: Cameron Makin
# Copyright: Wireless@VT
# Description: Uses 1 USRP to TX and RX on different channels
# GNU Radio version: 3.8.2.0 

from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time


class TXRX_USRP(gr.top_block):
    """
    Class Representing a USRP TX & RX Flowgraph.

    This flowgraph works for any USRPs that have multiple channels/radios that support simultaneous TX and RX. 
    
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


def main():

    tb = TXRX_USRP()

    tb.start()

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
