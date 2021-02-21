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

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget

from gnuradio import qtgui

class TXRX_USRP(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Full-Duplex TX and RX USRP")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Full-Duplex TX and RX USRP")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "TXRX_USRP")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.src_amp = src_amp = 0
        self.rx_bw = rx_bw = 10000000
        self.gain_tx_id = gain_tx_id = 31.5
        self.gain_rx_id = gain_rx_id = 0
        self.fc = fc = 915000000
        self.bw = bw = 5000000
        self.bins = bins = 1024
        self.X310_ip_address = X310_ip_address = "addr=192.168.40.203"

        ##################################################
        # Blocks
        ##################################################
        self._src_amp_range = Range(0, 1, 0.1, 0, 10)
        self._src_amp_win = RangeWidget(self._src_amp_range, self.set_src_amp, 'Signal Source Amplitude', "counter_slider", float)
        self.top_grid_layout.addWidget(self._src_amp_win)
        self._gain_tx_id_range = Range(0, 32, 0.5, 31.5, 200)
        self._gain_tx_id_win = RangeWidget(self._gain_tx_id_range, self.set_gain_tx_id, 'gain_tx', "counter_slider", float)
        self.top_grid_layout.addWidget(self._gain_tx_id_win)
        self._gain_rx_id_range = Range(0, 34, 0.5, 0, 200)
        self._gain_rx_id_win = RangeWidget(self._gain_rx_id_range, self.set_gain_rx_id, 'gain_rx', "counter_slider", float)
        self.top_grid_layout.addWidget(self._gain_rx_id_win)
        self._fc_range = Range(913000000, 917000000, 100000, 915000000, 200)
        self._fc_win = RangeWidget(self._fc_range, self.set_fc, 'center_freq', "counter_slider", float)
        self.top_grid_layout.addWidget(self._fc_win)
        self._bw_range = Range(1000000, 9000000, 100000, 5000000, 200)
        self._bw_win = RangeWidget(self._bw_range, self.set_bw, 'bandwidth', "counter_slider", float)
        self.top_grid_layout.addWidget(self._bw_win)
        self.uhd_usrp_source_1 = uhd.usrp_source(
            ",".join((X310_ip_address, "B:")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_1.set_center_freq(fc, 0)
        self.uhd_usrp_source_1.set_gain(gain_rx_id, 0)
        self.uhd_usrp_source_1.set_antenna('RX2', 0)
        self.uhd_usrp_source_1.set_bandwidth(rx_bw, 0)
        self.uhd_usrp_source_1.set_samp_rate(rx_bw)
        self.uhd_usrp_source_1.set_time_unknown_pps(uhd.time_spec())
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join((X310_ip_address, "A:")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_center_freq(fc, 0)
        self.uhd_usrp_sink_0.set_gain(gain_tx_id, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_bandwidth(bw, 0)
        self.uhd_usrp_sink_0.set_clock_rate(200e6, uhd.ALL_MBOARDS)
        self.uhd_usrp_sink_0.set_samp_rate(bw)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec())
        self.rx_probe = blocks.probe_signal_vf(bins)
        self.fft_vxx_0 = fft.fft_vcc(bins, True, window.blackmanharris(bins), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, bins)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, bins, 0)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(bins)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_UNIFORM, src_amp, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.rx_probe, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_stream_to_vector_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "TXRX_USRP")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_src_amp(self):
        return self.src_amp

    def set_src_amp(self, src_amp):
        self.src_amp = src_amp
        self.analog_noise_source_x_0.set_amplitude(self.src_amp)

    def get_rx_bw(self):
        return self.rx_bw

    def set_rx_bw(self, rx_bw):
        self.rx_bw = rx_bw
        self.uhd_usrp_source_1.set_samp_rate(self.rx_bw)
        self.uhd_usrp_source_1.set_bandwidth(self.rx_bw, 0)

    def get_gain_tx_id(self):
        return self.gain_tx_id

    def set_gain_tx_id(self, gain_tx_id):
        self.gain_tx_id = gain_tx_id
        self.uhd_usrp_sink_0.set_gain(self.gain_tx_id, 0)

    def get_gain_rx_id(self):
        return self.gain_rx_id

    def set_gain_rx_id(self, gain_rx_id):
        self.gain_rx_id = gain_rx_id
        self.uhd_usrp_source_1.set_gain(self.gain_rx_id, 0)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.uhd_usrp_sink_0.set_center_freq(self.fc, 0)
        self.uhd_usrp_source_1.set_center_freq(self.fc, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.uhd_usrp_sink_0.set_samp_rate(self.bw)
        self.uhd_usrp_sink_0.set_bandwidth(self.bw, 0)

    def get_bins(self):
        return self.bins

    def set_bins(self, bins):
        self.bins = bins

    def get_X310_ip_address(self):
        return self.X310_ip_address

    def set_X310_ip_address(self, X310_ip_address):
        self.X310_ip_address = X310_ip_address





def main(top_block_cls=TXRX_USRP, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
