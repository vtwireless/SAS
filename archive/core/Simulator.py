#!/usr/bin/env python3
"""
Main file to set up various environmental parameters for server and CBSD simulation.
Includes user registration and submitting various environment variables.
Additional enhancements can be made in primary user generation and simulated spectrum access measure reports. 

Revised: March 20, 2021
Authored by: Cameron Makin (cammakin8@vt.edu), Joseph Tolley (jtolley@vt.edu)
Advised by Carl Dietrich (cdietric@vt.edu)
For Wireless@VT
"""

from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import random
import socketio
import json
import sys
import csv
import time
import threading
from Server_WinnForum import RegistrationRequest, InstallationParam, RcvdPowerMeasReport, MeasReport
from argparse import ArgumentParser # If we want command line args

#global flags
printToCSV = False

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
parser.add_argument('-s', '--simulation', help="Relative path to simulation file", default=None)
parser.add_argument('--printToCSV', action='store_true')

#------------------------------------------------------------------------------------------

# Create a Global accessor for each Simulation
sim_one = None
timeDifferenceBetweenServerAndSimClient = 0
server_data = {}

# Helper Functions -------------------------------------------------------------------------
def delayUntilTime(lastTime, currentTime, socket):
	try:
		currentTime = int(currentTime)
	except:
		print("Could not convert 'time' key into an integer.")
		return None
    # while(True):
    #     nowTime = time.now()
	time.sleep(currentTime - lastTime)
	return currentTime
#------------------------------------------------------------------------------------------

class User:
    def __init__(self, id, isMU, percentageMUActive, latitude, longitude, secure, isMobile=False):
        self.id = id
        self.isMU = isMU
        self.percentageMUActive = percentageMUActive
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
    def __init__(self, numberOfUsers, percentageMU, percentMUActive, varianceOfData, percentageMobile, secureCount, socketObj, sim_steps):
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
        self.percentageMUActive = percentMUActive
        self.percentageMobile = percentageMobile
        self.secureCount = secureCount
        self.socket = socketObj
        self.sim_steps = sim_steps
        self.activePUCount = 0
        self.reportId = 0
        self.sim_log = {}

        #assumes this is for one channel

        numberMU = numberOfUsers*(percentageMU/100.0)
        sc = 0
        for x in range(numberOfUsers):
            if self.percentageMobile < random.randrange(0, 100):
                mobile = True
            else:
                mobile = False
            if x < numberMU:#malicious node
                self.createUser("", True, self.percentageMUActive, self.generateLat(), self.generateLon(), False, mobile)
            else:
                if sc < self.secureCount:#is secure
                    self.createUser("", False, 0, self.generateLat(), self.generateLon(), True, False)
                    sc = sc + 1 # Right?
                else:#regular node
                    self.createUser("", False, 0, self.generateLat(), self.generateLon(), False, mobile)

    def exit(self):
        """Exits Simulation"""
        time.sleep(2)
        self.socket.disconnect()
        sys.exit("Exiting Simulation")

    def run(self):
        """Queues up each simulation step in a delayed thread"""
        waitForSim = 0
        print("STARTING A SIM")
        for timeToExecute in self.sim_steps:
            waitForSim = float(timeToExecute)
            for action in self.sim_steps[timeToExecute]:
                if(action == "createPu"):
                    threading.Timer(float(timeToExecute)+0.01, self.createPU).start()
                    # self.createPU()
                elif(action == "normalSpectrum"):
                    threading.Timer(float(timeToExecute)+0.1, self.normalSpectrum).start()
                    # self.normalSpectrum()
                # elif(action == "pause"):
                #     threading.Timer(float(timeToExecute), time.sleep, args=[10]).start()
                #     # time.sleep(10)
                elif(action == "exit"):
                    threading.Timer(float(timeToExecute)+0.001, self.exit).start()
        time.sleep(waitForSim)

    def createUser(self, id, isMU, percentageMUActive, latitude, longitude, secure, isMobile):
        newUser = User(id, isMU, percentageMUActive, latitude, longitude, secure, isMobile)
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
        return (val*(mult/10))/10000

    def makePUData(self):
        arr = []
        for _ in range(self.arraySize):
            arr.append(self.makeData(self.PULow, self.PUHigh))
        return arr

    def createPU(self):
        # print("PU active")
        self.activePUCount = self.activePUCount + 1
        for user in self.users:
            if not user.isMU:
                self.sendData(user, self.makePUData())
            else:
                x = random.randrange(0,100)
                if x <= user.percentageMUActive:#if user is malicious send malicious
                    self.sendData(user, self.makeGoodData())
                else:
                    self.sendData(user, self.makePUData())
        self.socket.emit("simCheckPUAlert", json.dumps({"reportId":str(self.reportId)}))
        # formattedTime = str(float("{:0.3f}".format(time.time())))
        # print("ReportID: "+str(self.reportId)+" - Adding PU at time: "+ formattedTime)

        # This report should only go with 1 channel (the 1st one)
        self.sim_log[str(self.reportId)] = "1"
        self.reportId = self.reportId + 1

    def normalSpectrum(self):
        # print("Normal environment")
        for user in self.users:
            if not user.isMU:
                self.sendData(user, self.makeGoodData())
            else:
                x = random.randrange(0,100)
                if x <= user.percentageMUActive:#if user is malicious send malicious
                    self.sendData(user, self.makePUData())
                else:
                    self.sendData(user, self.makeGoodData())
        self.socket.emit("simCheckPUAlert", json.dumps({"reportId":str(self.reportId)}))
        self.sim_log[str(self.reportId)] = "0"
        self.reportId = self.reportId + 1


    def sendData(self, user, data):
        payload = []
        report = {}
        freqPerReport = 10000000/self.arraySize # 625000 for arraySize=16
        iter = 0
        for data_point in data:
            payload.append(RcvdPowerMeasReport(measFrequency=str((iter*624999)+3550000000),measBandwidth=freqPerReport,measRcvdPower=data_point))
            # if(printToCSV):
            #     report[str((iter*625000)+3550000000)] = data_point
            iter = iter + 1
        
        self.socket.emit("spectrumData", json.dumps({"spectrumData":{"cbsdId":user.id,"latitude":user.latitude, "longitude":user.longitude, "spectrumData": MeasReport(payload).asdict()}}))
        # self.socket.emit("simCheckPUAlert", json.dumps({"reportId":str(self.reportId)}))
        # if(isPuData):
        #     formattedTime = str(float("{:0.3f}".format(time.time())))
        #     print("ReportID: "+str(self.reportId)+" - Adding PU at time: "+ formattedTime)

        # # This report should only go with 1 channel (the 1st one)
        # self.sim_log[str(self.reportId)] = str(int(isPuData))

       # Global flag to print emitted data to a CSV 
        # if(printToCSV):
        #     with open('reports/output.csv', 'w', newline='') as csvfile:
        #         csvwriter = csv.writer(csvfile)
        #         for data in report:
        #             csvwriter.writerow([data, report[data]])

        # with open('student.json','w') as student_dumped :
        #     json.dump(student,student_dumped)
        # self.reportId = self.reportId + 1

    def move(self):
        for user in self.users:
            if user.mobile:
                user.latitude = self.generateLat()
                user.longitude = self.generateLon()

def calculateTimeDifference(data):
    payload = json.loads(data)
    if(serverTime := payload["serverCurrentTime"]):
        global timeDifferenceBetweenServerAndSimClient
        simtime = time.time()
        timeDifferenceBetweenServerAndSimClient = simtime-float(serverTime)
    print("Server: " + str(serverTime))
    print("Simulation: " + str(simtime))
    print("Difference: " + str(timeDifferenceBetweenServerAndSimClient))

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
    def detections(data):
        global server_data
        server_data = json.loads(data)
    
    @clientio.event
    def latencyTest(data):
        calculateTimeDifference(data)

    def hideComments():
        pass
        # @clientio.event
        # def spectrumInquiryResponse(data):
        #     if(nodes_awaiting_response):
        #         handleSpectrumInquiryResponse(clientio, data)
        #         global __blocked
        #         __blocked = False
        #     else:
        #         print("No Nodes are awaiting a SAS response. Ignoring Spectrum Inquiry Response from SAS.")

        # @clientio.event
        # def grantResponse(data):
        #     if(nodes_awaiting_response):
        #         handleGrantResponse(clientio, data)
        #         global __blocked
        #         __blocked = False
        #     else:
        #         print("No Nodes are awaiting a SAS response. Ignoring Grant Response from SAS.")

        # @clientio.event
        # def heartbeatResponse( data):
        #     if(nodes_awaiting_response):
        #         handleHeartbeatResponse(clientio, data)
        #         global __blocked
        #         __blocked = False
        #     else:
        #         print("No Nodes are awaiting a SAS response. Ignoring Heartbeat Response from SAS.")

        # @clientio.event
        # def relinquishmentResponse(data):
        #     if(nodes_awaiting_response):		
        #         handleRelinquishmentResponse(clientio, data)
        #         global __blocked
        #         __blocked = False
        #     else:
        #         print("No Nodes are awaiting a SAS response. Ignoring Relinquishment  Response from SAS.")

        # @clientio.event
        # def deregistrationResponse(data):
        #     if(nodes_awaiting_response):
        #         handleDeregistrationResponse(clientio, data)
        #         global __blocked
        #         __blocked = False
        #     else:
        #         print("No Nodes are awaiting a SAS response. Ignoring Deregistration Response from SAS.")
        # # end official WinnForum functions

        # @clientio.event
        # def changeRadioParams(data):
        #     """
        #     SAS command to change RX Parameters for a Node with a cbsdId.
        #     Calls 'updateRxParams(data)'

        #     Parameters
        #     ----------
        #     data : dictonary
        #         Expected keys are cbsdId, highFreq, and lowFreq
        #     """
        # 	# updateRxParams(data)
        #     pass # TODO

    @clientio.event
    def disconnect():
        """
        SAS Command to tell the socket connection to close
        """
        print('Connection to SAS terminating')
        # print("Exiting System...")
        # sys.exit()

def getDetections():
    correctDetections = 0
    falseDetections  = 0
    missedDetections = 0
    for key in sim_one.sim_log: # For every spectrum the sim sent
        try:
            if(server_data[key]):
                if(sim_one.sim_log[key] == "1"): # If they both detected PU
                    correctDetections = correctDetections + 1
                elif(sim_one.sim_log[key] == "0"): # Misdection
                    falseDetections = falseDetections + 1
            else:
                if(sim_one.sim_log[key] == "1"): # If there was infact a PU
                    missedDetections = missedDetections + 1
        except KeyError:
            print("server did not make any attempt at including the missed key. error.")
    return correctDetections, falseDetections, missedDetections

def printResults(numberOfUsers, percentageMU, percentageMUActive, varianceOfData, percentageMobile, secureCount, sim_path):
    correctDetections, falseDetections, missedDetections = getDetections()
    print("\nREPORT")
    print("# Users: "+str(numberOfUsers)+"\t%MU: "+str(percentageMU)+
    ", %Active: "+str(percentageMUActive)+"\tVariance: "+str(varianceOfData))
    # print(server_data)
    # print(sim_one.sim_log)
    print("TOTAL PU COUNT: " + str(sim_one.activePUCount))
    print("CORRECT DETECTIONS: " + str(correctDetections))
    print("FALSE DETECTIONS: " + str(falseDetections))
    print("MISSED DETECTIONS: " + str(missedDetections))

def resetTrackers():
    global server_data
    sim_one.activePUCount = 0
    sim_one.reportId = 0
    sim_one.sim_log = {}
    server_data = {}

def main(args):

    # Connect to SAS Server
    clientio = socketio.Client()  # Create Client Socket
    defineSocketEvents(clientio)  # Define handlers for events the SAS may emit
    socket_addr = 'http://' + args['address'] +':' + args['port']
    clientio.connect(socket_addr) # Connect to SAS

    # clientio.emit("latencyTest")

    # Get CLI Args
    printToCSV          = bool(args['printToCSV'])
    path                = args['simulation']    # Load Simulation steps from file

    global sim_one
    if(path): # If looping path is provided, then run multiple simulations
        try:
            with open(path) as config:
                sim_data = json.load(config)
        except:
            sys.exit("Fatal Error: No valid file found at "+str(path)+"\nExiting program...")
        for entry in sim_data[""]:
            numberOfUsers       = int(entry["numberOfUsers"])
            percentageMU        = float(entry["percentageMU"])
            percentageMUActive  = float(entry["percentageMUActive"])
            varianceOfData      = float(entry["varianceOfData"])
            percentageMobile    = float(entry["percentageMobile"])
            secureCount         = int(entry["secureCount"])
            sim_path            = entry["sim_steps"]
            try:
                with open(sim_path) as config:
                    sim_steps = json.load(config)
            except:
                sys.exit("Fatal Error: No valid simulation file found at "+str(sim_path)+"\nExiting program...")
            sim_one = Simulator(numberOfUsers, percentageMU, percentageMUActive, varianceOfData, percentageMobile, secureCount, clientio, sim_steps)
            for _ in range(int(entry["loop_count"])):
                sim_one.run()
                time.sleep(0.5)
                clientio.emit("getPuDetections") # At end of test run ask server to send over results
                time.sleep(1)# wait for server_data to be filled
                printResults(numberOfUsers, percentageMU, percentageMUActive, 
                varianceOfData, percentageMobile, secureCount, sim_path)
                resetTrackers()
        sim_one.exit()
    else:
        sys.exit("CLI Argument '--simulation' is required")

    # Insert graceful exit implementation
    return 0

if __name__ == "__main__":
    args = vars(parser.parse_args())	# Get command line arguments
    main(args)
