from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import random
import socketio
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


class Simulator:
    def __init__(self, numberOfUsers, percentageMU, varianceOfData, percentageMobile, secureCount):
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

        #assumes this is for one frequency range

        numberMU = numberOfUsers*(percentageMU/100)
        # mobile = False
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




    def createUser(self, id, isMU, percentageMU, latitude, longitude, secure, isMobile):
        self.users.append(User("", isMU, percentageMU, latitude, longitude, secure, isMobile))


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
                sendData(user, self.makePUData())
            else:
                x = random.randrange(0,100)
                if x < user.percentageMU:#if user is malicious send malicious
                    sendData(user, self.makeGoodData()())
                else:
                    sendData(user, self.makePUData()())


    def normalSpectrum(self):
        print("Normal environment")
        for user in self.users:
            if not user.isMU:
                sendData(user, self.makeGoodData())
            else:
                x = random.randrange(0,100)
                if x < user.percentageMU:#if user is malicious send malicious
                    sendData(user, self.makePUData()())
                else:
                    sendData(user, self.makeGoodData()())


    def sendData(self, user, data):
        print("todo")

    def move(self):
        for user in self.users:
            if user.mobile:
                user.latitude = self.generateLat()
                user.longitude = self.generateLon()


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
		if(nodes_awaiting_response):
			handleRegistrationResponse(clientio, data)
			global __blocked
			__blocked = False
		else:
			print("No Nodes are awaiting a SAS response. Ignoring Registration Response from SAS.")

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
		updateRxParams(data)

	@clientio.event
	def disconnect():
		"""
		SAS Command to tell the socket connection to close
		"""
		print('Connection to SAS terminating')
		print("Exiting System...")
		sys.exit()


def main(args):
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

    sim_one = Simulator(numberOfUsers, percentageMU, varianceOfData, percentageMobile, secureCount)

    # Insert gracfully exit implementation


if __name__ == "__main__":
    args = vars(parser.parse_args())	# Get command line arguments
    main(args)
