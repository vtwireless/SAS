#!/usr/bin/env python3

# import time
import json
import argparse
import socketio
from rx_usrp import rx_usrp

# TODO: Dynamic Socket Addressing (Want to be able to switch address/port of socket on the fly)

# Example Command to activate_rx: sas_test_server must be activate_rxning before entering this cmd
# ./socket_rx.py -p 5000 -a 127.0.0.1 -d "192.168.40.105" --freq 914.5 --bandwidth 0.1 --bins 100


# Parser extracts command line flags/parameters  
parser = argparse.ArgumentParser(description='SAS USRP RX Interface Script - Provide a server address and port in order to send spectral data (FFT Vector).')

# USRP Params---------------------------------------------------------------------------
parser.add_argument('-f','--freq',\
        help='Center frequency in Hz. Example: -f 914500000',\
        default=914.5)
parser.add_argument('-s','--samplerate',\
        help='Sample Rate Hz. Example: -s 1000000',\
        default=1.0)
parser.add_argument('-b','--bandwidth',\
        help='Bandwidth in Hz. Example: -b 50000',\
        default=0.5)
parser.add_argument('-n','--bins',\
        help='Number of FFT bins.  More for higher accuracy. Example: -n 80',\
        default=8)
parser.add_argument('-g','--gain',\
        help='Receiver Gain. Example: -g 1.0',\
        default=0.0)
parser.add_argument('-d','--device',\
        help='UHD USRP device IP address. Example: -d \'192.168.10.3\'',\
        default='192.168.10.3')
#----------------------------------------------------------------------------------------

# Socket Params----------------------------------------------------------------------------
parser.add_argument('-a','--address',\
        help='Server address to send spectrum data to. Env SERVER_ADDRESS will override this value. Example: -a 127.0.0.1',\
        default='127.0.0.1')
parser.add_argument('-p','--port',\
        help='Server port. Env SPECTRUM_PORT will override this value. Example: -p 65432',\
        default='5000')
#------------------------------------------------------------------------------------------

def send_params(clientio, rxUsrp):
    """
    Sends server the operating parameters of RX node
    """
    
    data = {
        "SDR Address": rxUsrp.get_SDR_Address(),
        "Center Frequency": rxUsrp.get_freq(),
        "Sample Rate": rxUsrp.get_signal_amp(),
        "Bandwidth": rxUsrp.get_bandwidth(),
        "Gain": rxUsrp.get_gain()
    }

    payload = json.dumps(data)
    clientio.echo("getParams", payload)

def send_spectrum(clientio, rxUsrp):
    """
    Sends FFT array as JSON to server

    Parameters
    ----------
    clientio : socket object
        socket connection to host
    rxUsrp : Rx USRP object
        Instance of Rx USRP object
    cFreq : double
        Center Frequency of receiver
    bandwidth : double
        bandwidth of the signal you want to receive
    """

    # old_data = {
    #     "Center Frequency": cFreq,
    #     "Bandwidth": bandwidth,
    #     "FFT": list(rxUsrp.blocks_probe_signal_vx_0.level())
    # }

    data = {
        "FFT": list(rxUsrp.blocks_probe_signal_vx_0.level())
    }

    payload = json.dumps(data)
    clientio.echo("spectrumUpdate", payload)


def update_params(rxUsrp, newParams):
    """
    Updates RX parameters 
    """

    # check params for every key:value pair
    params = json.loads(newParams)
    if "freq" in params:
        rxUsrp.set_freq(float(params['freq']))
    if "bandwidth" in params:
        rxUsrp.set_bandwidth(float(params['bandwidth']))
    if "gain" in params:
        rxUsrp.set_gain(float(params['gain']))
    if "sample_rate" in params:
        rxUsrp.set_sample_rate(float(params['sample_rate']))

    # Send server updated params?
    # TODO

def define_socket_events(clientio, rxUsrp):
    """
    """
    #########################
    # List of Socket Events #
    #########################
    @clientio.event
    def connect():
        print('connection established. Given sid: ' + clientio.sid)

    @clientio.event
    def identifySource():
        clientio.emit("identifySource", ("I am a CORENET node with device addr: " + rxUsrp.get_SDR_Address()))
        send_params(clientio, rxUsrp)
        registrationRequest(clientio)

    #
    # Official WinnForum Predefined Functionality
    # 

    @clientio.event
    def registrationResponse(data):
        handleRegistrationResponse(clientio, data)
    
    @clientio.event
    def sprectumInquiryResponse(data):
        handleSpectrumInquiryResponse(clientio, data)
    
    @clientio.event
    def grantResponse(data):
        handleGrantResponse(clientio, data)

    @clientio.event
    def heartbeatResponse(data):
        handleHeartbeatResponse(clientio, data)

    @clientio.event
    def relinquishmentResponse(data):
        handleRelinquishmentResponse(clientio, data)

    @clientio.event
    def deregistrationResponse(data):
        handleDeregistrationResponse(clientio, data)
    # end official WinnForum functions

    @clientio.event
    def getTxParams():
        send_params(clientio, rxUsrp)

    @clientio.event
    def updateParams(newParams):
        updateRadio(rxUsrp, newParams)

    @clientio.event
    def stop_radio():
        txUsrp.stop()

    @clientio.event
    def start_radio():
        txUsrp.start()      

    @clientio.event
    def disconnect():
        print('disconnected from server')

def init(clientio, args):
    """
    Initializing function where USRP is created and turned on.
    Socket connection to SAS is also created in this function.

    Parameters
    ----------
    clientio : socket object
        Socket where host can be reached
    args : list
        List of parameters extracted from command line flags   
    """

    sdrAddr     = args['device']
    freq        = float(args['freq'])
    sample_rate = float(args['samplerate'])
    bins        = int(args['bins']);
    bandwidth   = float(args['bandwidth'])
    gain        = args['gain']

    rxUsrp = rx_usrp(sdrAddr, freq, bins, sample_rate, bandwidth, gain) # Create instance of Rx with given parameters
    #    def __init__(self, deviceAddr, centerFreq, bins, bandwidth=0, sample_rate, gain=0):

    define_socket_events(clientio, rxUsrp)  

    # Connect to server
    socket_addr = 'http://' + args['address'] +':' + args['port']
    clientio.connect(socket_addr)


    rxUsrp.start() # Turn On Rx USRP
    # send_spectrum(clientio, rxUsrp, freq, bandwidth)


if __name__ == '__main__':
    args = vars(parser.parse_args())    # Get command line arguments
    clientio = socketio.Client()        # Create Client Socket
    init(clientio, args)                # Init Rx USRP and Socket
    clientio.wait()                     # Wait for Socket Events
