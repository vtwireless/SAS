from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import random
import socketio
import json
import sys
import time
from WinnForum import RegistrationRequest, InstallationParam, RcvdPowerMeasReport, MeasReport
from argparse import ArgumentParser # If we want command line args


# Parser extracts command line flags/parameters  
parser = ArgumentParser(description='Testbench-to-SAS Client Script - Provide a server address and port in order to connect to the SAS.')

# Socket Params----------------------------------------------------------------------------
parser.add_argument('-a','--address',\
		help='Server address. Example: -a \'127.0.0.1\'',\
		default='localhost')
parser.add_argument('-p','--port',\
		help='Server port. Example: -p 65432',\
		default='8000')
#------------------------------------------------------------------------------------------

# Simulation Args --------------------------------------------------------------------------
parser.add_argument('--numberOfUsers',default=10)
parser.add_argument('--percentageMU',default=15)
parser.add_argument('--varianceOfData',default=5)
parser.add_argument('--percentageMobile',default=10)
parser.add_argument('--secureCount',default=1)
parser.add_argument('-s', '--simulation')
#------------------------------------------------------------------------------------------

# Create a Global accessor for each Simulation
sim_one = None

# Helper Functions -------------------------------------------------------------------------
def delayUntilTime(lastTime, currentTime):
	try:
		currentTime = int(currentTime)
	except:
		print("Could not convert 'time' key into an integer.")
		return None
	time.sleep(currentTime - lastTime)
	return currentTime
#------------------------------------------------------------------------------------------

class User:
    def __init__(self, id, isMU, percentageMU, latitude, longitude, secure, isMobile=False):
        self.id = id
        self.isMU = isMU
        self.percentageMU = percentageMU
        self.latitude = latitude
        self.longitude = longitude
        self.secure = secure
        self.mobile = isMobile

    def registrationRequest(self):
        installationParam = InstallationParam(
            latitude=self.latitude, longitude=self.longitude)
        request = RegistrationRequest(
            userId=self.id, fccId="fakeFCCID", cbsdSerialNumber="fakeCBSDSerialNum",\
            cbsdCategory="X", installationParam=installationParam).asdict()
        return json.dumps({"registrationRequest": [request]})

    def handleRegistrationResponse(self, data):
        self.id = data["cbsdId"]
        

class Simulator:
    def __init__(self, numberOfUsers, percentageMU, varianceOfData, percentageMobile, secureCount, socketObj, sim_steps):
        """
        numberOfUsers (int) - how many users will be connecting to the SAS
        percentageMU (int [0,100]) - what percent chance of a user will be malicious
        varianceOfData - 
        percentageMobile - (does this include MUs?)
        secureCount - 
        """
        self.users = []
        self.numberOfUsers = numberOfUsers
        self.varianceOfData = varianceOfData
        self.goodLow = -70
        self.goodHigh = 25
        self.PULow = 27
        self.PUHigh = 40
        self.arraySize = 16
        self.percentageMU = percentageMU
        self.percentageMobile = percentageMobile
        self.secureCount = secureCount
        self.socket = socketObj
        self.sim_steps = sim_steps

        #assumes this is for one channel

        numberMU = numberOfUsers*(percentageMU/100)
        sc = 0
        for x in range(numberOfUsers):
            if self.percentageMobile < random.randrange(0, 100):
                mobile = True
            else:
                mobile = False
            if x < numberMU:#malicious node
                self.createUser("", True, self.percentageMU, self.generateLat(), self.generateLon(), False, mobile)
            else:
                if sc < self.secureCount:#is secure
                    self.createUser("", False, 0, self.generateLat(), self.generateLon(), True, False)
                    sc = sc + 1 # Right?
                else:#regular node
                    self.createUser("", False, 0, self.generateLat(), self.generateLon(), False, mobile)
        
    def exit(self):
        sys.exit("Exiting Simulation")
        
    def run(self):
        lastTime = 0
        for timeToExecute in self.sim_steps:
            lastTime = delayUntilTime(lastTime, timeToExecute)
            for action in self.sim_steps[timeToExecute]:
                pass # call appropoiate function
                if(action == "createPu"):
                    self.createPU()
                elif(action == "normalSpectrum"):
                    self.normalSpectrum()
        time.sleep(3)
        self.exit()

    def createUser(self, id, isMU, percentageMU, latitude, longitude, secure, isMobile):
        newUser = User("", isMU, percentageMU, latitude, longitude, secure, isMobile)
        self.users.append(newUser)
        self.socket.emit("registrationRequest", newUser.registrationRequest())


    def generateLat(self):
        lat = random.randrange(3722000,3723000)
        return (lat /100000)

    def generateLon(self):
        lon = random.randrange(8040000,8041000)
        lon = lon /100000
        return (-1 * lon)

    def makeGoodData(self):
        arr = []
        for _ in range(self.arraySize):
            arr.append(self.makeData(self.goodLow, self.goodHigh))
        return arr

    def makeData(self, low, high):
        val = random.randrange(low*10000, high*10000)
        mult = random.randrange(8, 12)
        return val*(mult/10)

    def makePUData(self):
        arr = []
        for _ in range(self.arraySize):
            arr.append(self.makeData(self.PULow, self.PUHigh))
        return arr

    def createPU(self):
        print("PU active")
        for user in self.users:
            if not user.isMU:
                self.sendData(user, self.makePUData())
            else:
                x = random.randrange(0,100)
                if x < user.percentageMU:#if user is malicious send malicious
                    self.sendData(user, self.makeGoodData())
                else:
                    self.sendData(user, self.makePUData())

    def normalSpectrum(self):
        print("Normal environment")
        for user in self.users:
            if not user.isMU:
                self.sendData(user, self.makeGoodData())
            else:
                x = random.randrange(0,100)
                if x < user.percentageMU:#if user is malicious send malicious
                    self.sendData(user, self.makePUData())
                else:
                    self.sendData(user, self.makeGoodData())

    def sendData(self, user, data):
        payload = []
        freqPerReport = 10000000/self.arraySize # 625000 for arraySize=16
        for data_point in data:
            payload.append(RcvdPowerMeasReport(measFrequency=data_point*625000,measBandwidth=freqPerReport,measRcvdPower=data_point))
        self.socket.emit("spectrumData", json.dumps({"spectrumData":{"cbsdId":user.id,"spectrumData": MeasReport(payload).asdict()}}))

    def move(self):
        for user in self.users:
            if user.mobile:
                user.latitude = self.generateLat()
                user.longitude = self.generateLon()


def handleRegistrationResponse(clientio, data):
    payload = json.loads(data)
    for user in sim_one.users:
        if(user.id == ""):
            user.handleRegistrationResponse(payload["registrationResponse"][0])
            break

def defineSocketEvents(clientio):
    """
    List of events the SAS may emit, and functions to call to handle them

    Parameters
    ----------
    clientio : socketio Client object
        socket to SAS
    """
    @clientio.event
    def connect():
        print('Socket connection established! Given sid: ' + clientio.sid)

    # @clientio.event
    # def identifySource():
    # 	clientio.emit("identifySource", ("I am CRTS"))

    # Official WinnForum Predefined Functionality
    @clientio.event
    def registrationResponse(data):
        # if(nodes_awaiting_response):
            handleRegistrationResponse(clientio, data)
            # global __blocked
            # __blocked = False
        # else:
            # print("No Nodes are awaiting a SAS response. Ignoring Registration Response from SAS.")

    @clientio.event
    def spectrumInquiryResponse(data):
        if(nodes_awaiting_response):
            handleSpectrumInquiryResponse(clientio, data)
            global __blocked
            __blocked = False
        else:
            print("No Nodes are awaiting a SAS response. Ignoring Spectrum Inquiry Response from SAS.")

    @clientio.event
    def grantResponse(data):
        if(nodes_awaiting_response):
            handleGrantResponse(clientio, data)
            global __blocked
            __blocked = False
        else:
            print("No Nodes are awaiting a SAS response. Ignoring Grant Response from SAS.")

    @clientio.event
    def heartbeatResponse( data):
        if(nodes_awaiting_response):
            handleHeartbeatResponse(clientio, data)
            global __blocked
            __blocked = False
        else:
            print("No Nodes are awaiting a SAS response. Ignoring Heartbeat Response from SAS.")

    @clientio.event
    def relinquishmentResponse(data):
        if(nodes_awaiting_response):		
            handleRelinquishmentResponse(clientio, data)
            global __blocked
            __blocked = False
        else:
            print("No Nodes are awaiting a SAS response. Ignoring Relinquishment  Response from SAS.")

    @clientio.event
    def deregistrationResponse(data):
        if(nodes_awaiting_response):
            handleDeregistrationResponse(clientio, data)
            global __blocked
            __blocked = False
        else:
            print("No Nodes are awaiting a SAS response. Ignoring Deregistration Response from SAS.")
    # end official WinnForum functions

    @clientio.event
    def changeRadioParams(data):
        """
        SAS command to change RX Parameters for a Node with a cbsdId.
        Calls 'updateRxParams(data)'

        Parameters
        ----------
        data : dictonary
            Expected keys are cbsdId, highFreq, and lowFreq
        """
		# updateRxParams(data)
        pass # TODO

    @clientio.event
    def disconnect():
        """
        SAS Command to tell the socket connection to close
        """
        print('Connection to SAS terminating')
        print("Exiting System...")
        sys.exit()

def main(args):

    # Load Simulation steps from file
    path = args['simulation']
    try:
        with open(path) as config:
            sim_steps = json.load(config)
    except:
        sys.exit("Fatal Error: No valid simulation file found at "+str(path)+"\nExiting program...")

    clientio = socketio.Client()  # Create Client Socket
    defineSocketEvents(clientio)  # Define handlers for events the SAS may emit
    socket_addr = 'http://' + args['address'] +':' + args['port']
    clientio.connect(socket_addr) # Connect to SAS

    # Pulls values for Simulation from commandline
    # Top of this script allows you to set default values for these
    numberOfUsers = int(args['numberOfUsers'])
    percentageMU = float(args['percentageMU'])
    varianceOfData = float(args['varianceOfData'])
    percentageMobile = float(args['percentageMobile'])
    secureCount = float(args['secureCount']) # or int?

    global sim_one
    sim_one = Simulator(numberOfUsers, percentageMU, varianceOfData, percentageMobile, secureCount, clientio, sim_steps)
    sim_one.run()

    # Insert graceful exit implementation
    return 0

if __name__ == "__main__":
    args = vars(parser.parse_args())	# Get command line arguments
    main(args)
