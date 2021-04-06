#!/usr/bin/env python3

# Title: CORNET-to-SAS Client
# Author: Cameron Makin
# For Research Efforts: Wireless@VT
# Description: This is the main script to execute in order to create a client connection to a SAS.
# Last Updated: 03/04/2021

# TODO: Dynamic Socket Addressing (Want to be able to switch address/port of socket on the fly)
# TODO: Decide how SAS assigned info (i.e. cbsdId) is stored
# TODO: Create some command line keyword that works at all instances to exit from the prompt...
# TODO: Create a function to handle the "response" field from all the SAS responses
# TODO: Maybe add menu option to view all history to see what has been done and their responses
#./socket_tx.py -p 5000 -a "127.0.0.1"

import sys
import json
import time
import socketio
import threading
from argparse import ArgumentParser
from datetime import datetime, timedelta
from gnuradio import uhd
from usrps import Node
from WinnForum import *		# File containing object definitions used
from cmd_prompts import * 	# User defined module for cmd prompts

# Globals
# blocked: Used to ensure recieved socket messages display on the terminal before the main menu blocks the command-line interface .
# This variable is set to 'True' right before a client emit with an expected response executes. The response will set it back to False.
__blocked = False

# sim_mode: Used to ensure functions do not attempt blocking user-input features.
__sim_mode = False

# created_nodes: holds all created CRTS USRP Nodes objects
created_nodes = []

# registered_nodes: Nodes that are SAS registered
registered_nodes = []

# nodes_awaiting_response: Holds Nodes that have sent a request to the SAS and are waiting for a response
nodes_awaiting_response = []

# Parser extracts command line flags/parameters  
parser = ArgumentParser(description='CORNET-to-SAS Client Script - Provide a server address and port in order to connect to the SAS.')

# Socket Params----------------------------------------------------------------------------
parser.add_argument('-a','--address',\
		help='Server address. Example: -a \'127.0.0.1\'',\
		default='localhost')
parser.add_argument('-p','--port',\
		help='Server port. Example: -p 65432',\
		default='8000')
#------------------------------------------------------------------------------------------

# Use Simulation File----------------------------------------------------------------------
parser.add_argument('-s','--sim',\
		help='Simulation File path (realative to socket_to_sas.py). Example: -s simulations/sim_one.json',\
		default=None)
#------------------------------------------------------------------------------------------

# Helper Functions-------------------------------------------------------------------------
def printNodeArray(whichArray):
	"""
	Prints out either create_nodes, registered_nodes, or nodes_awaiting_response to terminal

	Parameters
	----------
	whichArray : string
		Only possible values are "created", "registered", or "waiting"
	"""
	if(whichArray == "created"):
		nodeArray = created_nodes
		print("Showing Nodes that have been created:")
	elif(whichArray == "registered"):
		print("Showing Nodes that have been SAS Registered:")
		nodeArray = registered_nodes
	elif(whichArray == "waiting"):
		print("Showing Nodes that are waiting for a SAS Response:")
		nodeArray = nodes_awaiting_response
	else:
		print("Invalid parameter value passed to 'printNodeArray'.")
		return

	for node in nodeArray:
		node.info()

def _grabPossibleEntry(entry, key):
	"""
	Takes a dictionary entry and checks to see if it exists (e.g. check for entry[key]).

	Parameters
	----------
	entry : dictionary
		Dictonary to check for 'key'
	key : string
		String key for the dictonary

	Returns
	-------
	value : various types
		If entry exists, returns entry, otherwise return None
	"""
	try:
		return entry[key]
	except KeyError:
		return None
	except TypeError:
		return None

def findNodeAwaitingResponseByCbsdId(cbsdId):
	"""
	SAS Responses utilize cbsdId to ID which nodes go with which responses.
	This function accepts a cbsdId and returns the Node object it goes with.

	Parameters
	----------
	cbsdId : string
		CBSD ID of a desired Node awaiting a SAS response (i.e a node in nodes_awaiting_response)

	Returns
	-------
	node : Object
		The Node with the same cbsdId. Will return 'None' if no Node has the cbsdId.
	"""
	if(cbsdId):
		for node in nodes_awaiting_response:
			if(node.getCbsdId() == cbsdId):
				return node
	return None

def findRegisteredNodeByCbsdId(cbsdId):
	"""
	This function accepts a cbsdId and returns the Registered Node object it goes with.

	Parameters
	----------
	cbsdId : string
		CBSD ID of a desired SAS-Registered Node (i.e a node in registered_nodes)

	Returns
	-------
	node : Object
		The Node with the same cbsdId. Will return 'None' if no Node has the cbsdId.
	"""
	for node in registered_nodes:
		if(node.getCbsdId() == cbsdId):
			return node
	return None

def findCreatedNodeByIp(address):
	"""
	Returns a Node with the provided IP Address

	Parameters
	----------
	address : string
		IP Address of a created_node

	Returns
	-------
	node : Node object
		Node with the desired IP Address, or None
	"""
	for node in created_nodes:
		if(address == node.getIpAddress()):
			return node
	return None

def reqAddressToNode(request, mustBeRegistered=True):
	"""
	This finds an IP address from a Sim request, and returns the Node object with the same IP.

	Since the simulation file cannot identify Nodes by their cbsdIds that are dynamically assigned,
	the sim file uses the Node IP addresses to idenetify them. 
	This funciton helps by using the Node IP and returning the Node object, so that more info is available.
	This is desirable in all the Requests functions (hence this function beginning with 'req').

	Parameters
	----------
	request : dictionary
		A single request from a simulation file
	mustBeRegistered : boolean
		If True, only return back a Node obj if it has a cbsdId (i.e. if it is already registered)

	Returns
	-------
	node : Node object
		If a node match is found, return the Node, else return None
	"""
	if(not (address := _grabPossibleEntry(request, "nodeIp"))):
		print("No nodeIp address found.")
		return None
	if(not (node := findCreatedNodeByIp(address))):
		print("No Created Node was found with the IP Address: '" + address + "'.")
		return None
	if(mustBeRegistered and (not node.getRegistrationStatus())):
		print("Node found but not yet registered.")
		return None
	return node

def _hasResponseCode(data):
	"""
	This checks a dictonary for a key of "response" and a subkey of "responseCode".
	It returns the responseCode if it is found.

	Parameters
	----------
	data : dictonary 
		A dictionary that should have a key of "response"

	Returns
	-------
	responseCode : string
		Will return responseCode if it is there, otherwise 'None'
	"""
	if(response := _grabPossibleEntry(data, "response")):
		if(responseCode := _grabPossibleEntry(response, "responseCode")):
				return responseCode
		else:
			print("SASError: No response code provided.")
			return None
	else:
		print("SASError: No reponse object found.")
		return None

def _compileMeasReport(node, reportingAlgorithm="every64Bins"):
	"""
	Creates a MeasReport(array of RcvdPowerMeasReports) with the given Node's RX capabilities.
	RcvdPowerMeasReports will be broken into 1MHz reports (of average pwoer) regardless of RX bandwidth.
	This means each channel will be reported in 10 reports for inmproved spectrum estimation accuracy.

	Parameters
	---------
	node : Node object
		Node to create a MeasReport

	reportingAlgorithm : string
		This changes the way MeasReort is created. There are 4 proposed methods:
		"every64Bins" - Averages 64 bins per RcvdPowerMeasReport (default)
		"eachBin" - Sends every bin as a RcvdPowerMeasReport
		"oneMhzAtATime" - Averages the bins that are exclusive to each received 1MHz region into 1 RcvdPowerMeasReport
		"oneChannelAtATime" - Averages the bins that are exclusive to each received 10MHz channel into 1 RcvdPowerMeasReport
	
	Returns
	-------
	report : MeasReport object
	"""
	# Determine how many reports to create knowing the bandwidth
	# Math
	# if bwInMhz = 10, make 10 reports
	# Get bins
	# if bins = 1024 and bw = 10Mhz,
	# that means 1 bin = 10/1024 MHz
	#
	#
	#

	mode = node.getOperationMode()
	if(mode == "TXRX"):
		fc = node.getUsrp().get_rx_fc()
		bw = node.getUsrp().get_rx_bw()
		bins = node.getUsrp().get_rx_bins()
	elif(mode == "RX"):
		fc = node.getUsrp().get_fc()
		bw = node.getUsrp().get_bw()
		bins = node.getUsrp().get_bins()
	else:
		return None 

	data = node.getSpectrumProbeData()
	lowFreq = fc - (bw/2)
	# def HZ_TO_MHZ(hz):
	# 	return hz/1000000
	reports = []
	if(reportingAlgorithm == "every64Bins"):
		frequencyPerGroup = (bw/bins)*64
		reportStartFreq = lowFreq
		for eachGroup in range(int(bins/64)):
			startIndex = eachGroup*64
			averagePower = sum(data[int(startIndex):int(startIndex+64)])/64
			reports.append(RcvdPowerMeasReport(reportStartFreq, frequencyPerGroup, averagePower))	
	elif(reportingAlgorithm == "eachBin"):
		frequencyPerBin = bw/bins
		reportStartFreq = lowFreq
		for eachBin in bins:
			reports.append(RcvdPowerMeasReport(reportStartFreq, frequencyPerBin, data[eachBin]))
			reportStartFreq = reportStartFreq + frequencyPerBin
	elif(reportingAlgorithm == "oneMhzAtATime"):
		pass
	elif(reportingAlgorithm == "oneChannelAtATime"):
		pass

	return MeasReport(reports)

def unpackResponseWithKeys(response, *keys):
	"""
	Takes a response and returns the values of the desired keys by calling _grabPossibleEntry().
	The *keys parameter is important because you never know what keys the SAS will send.
	This will be sure to check for every expected key and return its value in order.

	Parameters
	----------
	response : dictonary
		A SAS response
	*keys : unknown number of strings
		These are the keys to specifically look for in a dictonary

	Returns
	-------
	arr : array of string
		An array holding the key values. 
	"""
	arr = []
	for key in keys:
		if(key == "responseCode"):
			arr.append(_hasResponseCode(response))
		else:
			arr.append(_grabPossibleEntry(response, key))
	return arr	

def safeCast(value, dataType):
	"""
	This method handles ValueError exceptions when casting data.

	Example: myInt = safeCast("12", int)

	Parameters
	----------
	value : any data type
		Piece of data that needs to be casted to a different type
	dataType : Python data type object
		Data type to cast 'value' to
	"""
	try:
		return dataType(value)
	except ValueError:
		print("Cannot cast '"+str(value)+"' to data type '"+str(dataType)+"'.")
		return None
# End Helper Functions---------------------------------------------------------------------

# Create Node------------------------------------------------------------------------------
def simCreateNode(requests):
	"""
	Creates node(s) based on simulation file

	TODO: Make sure the data can create a vaild USRP
	TODO: What params would RX need instead?
	TODO: Decide what KeyErrors should hault node creation

	Parameters
	----------
	requests : array of dictionaries 
		Node data for creation

	Returns
	-------
	arr : array of Node object(s)
	"""
	arr = []
	iter = 0
	for request in requests:
		print("Parsing through Create Node [" + str(iter := iter+1) + "]:")
		print(request)

		if(address := _grabPossibleEntry(request, "address")):
			# Ensure IP address is not in an already created_node
			if(findCreatedNodeByIp(address)):
				print("IP Address already belongs to a created Node. Node not created.")
				continue
		else:
			print("SimulationFileError: No address found for simCreateNode. Node not created.")
			continue
		
		if(not (usrpMode := _grabPossibleEntry(request, "mode"))):
			print("SimulationFileError: No usrp mode found for simCreateNode. Node not created.")
			continue
		elif(not (usrpMode == "TX" or usrpMode == "RX" or usrpMode == "TXRX")):
			print("SimulationFileError: Invalid mode '"+usrpMode+"' for simCreateNode. Node not created.")
			continue

		if(usrpMode == "TX"):
			if(not (centerFreq := safeCast(_grabPossibleEntry(request, "centerFreq"), int))):
				print("SimulationFileError: No valid integer 'centerFreq' found for simCreateNode. Node not created.")
				continue
			if(not (bandwidth := safeCast(_grabPossibleEntry(request, "bandwidth"), int))):
				print("SimulationFileError: No valid integer 'bandwidth' found for simCreateNode. Node not created.")
				continue
			if(not (waveform := _grabPossibleEntry(request, "waveform"))):
				print("SimulationFileError: No waveform found for simCreateNode. Node not created.")
				continue
			if(not (gain := safeCast(_grabPossibleEntry(request, "gain"), float))):
				print("SimulationFileWarning: No valid float 'gain' found for simCreateNode. Defaulting to 0.")
				gain = 0
			if(not (signalAmp := safeCast(_grabPossibleEntry(request, "signalAmp"), float))):
				print("SimulationFileWarning: No valid float signalAmp found for simCreateNode. Defaulting to 0.")
				signalAmp = 0

			node = Node(address)
			node.setOperationMode(usrpMode)
			node.createTxUsrp(centerFreq, gain, bandwidth, signalAmp, waveform)
			node.disableTx()
		elif(usrpMode == "RX"):
			if(not (centerFreq := safeCast(_grabPossibleEntry(request, "mode"), int))):
				print("SimulationFileError: No valid integer centerFreq found for simCreateNode. Node not created.")
				continue
			if(not (gain := safeCast(_grabPossibleEntry(request, "gain"), float))):
				print("SimulationFileWarning: No valid float gain found for simCreateNode. Defaulting to 0.")
				gain = 0
			if(not (bandwidth := safeCast(_grabPossibleEntry(request, "bandwidth"), int))):
				print("SimulationFileError: No valid integer bandwidth found for simCreateNode. Node not created.")
				continue

			node = Node(address)
			node.setOperationMode(usrpMode)
			node.createRxUsrp(int(centerFreq), float(gain), int(bandwidth))
		elif(usrpMode == "TXRX"):
			if(not (tx_fc := safeCast(_grabPossibleEntry(request, "tx_fc"), int))):
				print("SimulationFileError: No valid integer 'tx_fc' found for simCreateNode. Node not created.")
				continue
			if(not (tx_gain := safeCast(_grabPossibleEntry(request, "tx_gain"), float))):
				print("SimulationFileWarning: No valid float 'tx_gain' found for simCreateNode. Defaulting to 0.")
				tx_gain = 0
			if(not (tx_bw := safeCast(_grabPossibleEntry(request, "tx_bw"), int))):
				print("SimulationFileError: No valid integer 'tx_bw' found for simCreateNode. Node not created.")
				continue
			if(not (tx_src_amp := safeCast(_grabPossibleEntry(request, "tx_src_amp"), float))):
				print("SimulationFileError: No valid float 'tx_src_amp' found for simCreateNode. Node not created.")
				continue
			if(not (rx_fc := safeCast(_grabPossibleEntry(request, "rx_fc"), int))):
				print("SimulationFileError: No valid integer 'rx_fc' found for simCreateNode. Node not created.")
				continue
			if(not (rx_gain := safeCast(_grabPossibleEntry(request, "rx_gain"), float))):
				print("SimulationFileWarning: No valid float 'rx_gain' found for simCreateNode. Defaulting to 0.")
				rx_gain = 0
			if(not (rx_bw := safeCast(_grabPossibleEntry(request, "rx_bw"), int))):
				print("SimulationFileError: No valid integer 'rx_bw' found for simCreateNode. Node not created.")
				continue
			
			node = Node(address)
			node.setOperationMode(usrpMode)
			node.createTxRxUsrp(tx_fc, tx_bw, tx_src_amp, tx_gain, rx_fc, rx_bw, rx_gain)
			node.disableTx()
		node.getUsrp().start()
		arr.append(node)
	return arr

def cmdCreateNode():
	"""
	Walks a user through the command line to configure a USRP node.
	Appends a node to the global created_nodes list

	TODO: Ask user how many nodes they want to create and loop through N times
	TODO: Pass values to the prompt to check for boundaries
	"""
	sdrAddr = promptUsrpIpAddr()
	node = Node(sdrAddr)
	usrpMode = promptUsrpMode()
	if(usrpMode == "TXRX"):
		print("Enter TX Parameters for the follow inputs")
		tx_fc = promptUsrpCenterFreq()
		tx_gain = promptUsrpGain()
		tx_bw = promptUsrpBandwidth()
		tx_src_amp = promptUsrpSignalAmp()
		print("Enter RX Parameters for the remaining inputs")
		rx_fc = promptUsrpCenterFreq()
		rx_gain = promptUsrpGain()
		rx_bw = promptUsrpBandwidth()
		node.createTxRxUsrp(tx_fc, tx_bw, tx_src_amp, tx_gain, rx_fc, rx_bw, rx_gain)
		node.disableTx()
	elif(usrpMode == 'TX'):
		cFreq = promptUsrpCenterFreq()
		usrpGain = promptUsrpGain()
		bandwidth = promptUsrpBandwidth()
		signalAmp = promptUsrpSignalAmp()
		waveform = promptUsrpWaveform()
		node.createTxUsrp(cFreq, usrpGain, bandwidth, signalAmp, waveform)
		node.disableTx()
	elif(usrpMode == 'RX'):
		# cFreq = promptUsrpCenterFreq()
		# bandwidth = promptUsrpBandwidth()
		# usrpGain = promptUsrpGain()
		# node.getUsrp().start()
		pass # Big TODO
	else:
		print("Error: Invalid USRP mode. Exiting 'Create Node' operation.")
		return None
	node.getUsrp().start()
	return [node]

def createNode(requests=None):
	"""
	Function always called when creating new Nodes.
	Appends create_nodes array with new Nodes.
	USRPs for each Node will turn on after creation,
	but TX will have 0 amplitude so they will be "off".

	Parameters
	----------
	requests : array of Requests (optional)
		If simulation file is calling this function, requests is an array of >=1 node data.
		If this is being called by the cmd-line interface, requests should be 'None'
	"""
	if(__sim_mode):
		nodes = simCreateNode(requests)
	else:
		nodes = cmdCreateNode()

	for node in nodes:
		created_nodes.append(node)
# End Create Node--------------------------------------------------------------------------

# Registation ----------------------------------------------------------------------
def simRegistrationReq(requests):
	"""
	Simulation file provides data to create a Registration Request.

	Since there may be multiple registration requests at once, there is a for loop. 
	The value of 'request' should be a single registration request. 

	Parameters
	----------
	requests : array of dictionaries
		Registration Request data
	"""
	arr = []
	iter = 0
	for request in requests:
		print("\nCreating Registration Request [" + str(iter := iter+1) + "]:")
		print(request)
		if(not (node := reqAddressToNode(request, False))):
			print("Registration Request invalid.")
			continue
		if(not (cbsdSerialNumber := node.getSerialNumber())):
			print("No cbsdSerialNumber found for the node with IP Address: '"+str(node.getIpAddress())+"'. Registration Request invalid.")
			continue
		if(not (userId := _grabPossibleEntry(request, "userId"))):
			print("No userId found for simRegistrationReq. Registration Request invalid.")
			continue
		if(not (fccId := _grabPossibleEntry(request, "fccId"))):
			print("No fccId found for simRegistrationReq. Registration Request invalid.")
			continue
		callSign = _grabPossibleEntry(request, "callSign")
		cbsdCategory = _grabPossibleEntry(request, "cbsdCategory")
		# if(not cbsdCategory):
		# 	print("No cbsdCategory provided. Registration Request invalid.")
		# 	continue
		if(cbsdInfo := _grabPossibleEntry(request, "cbsdInfo")):
			cbsdInfo = CbsdInfo(
				_grabPossibleEntry(cbsdInfo, "vendor"),
				node.getModel(),
				_grabPossibleEntry(cbsdInfo, "softwareVersion"),
				_grabPossibleEntry(cbsdInfo, "hardwareVersion"),
				_grabPossibleEntry(cbsdInfo, "firmwareVersion")
			)
		airInterface = _grabPossibleEntry(request, "airInterface")
		airInterface = AirInterface(_grabPossibleEntry(airInterface, "radioTechnology"))
		# TODO: Determine the proper airInterfaces for the USRPs
		# if(not airInterface):
		# 	print("No airInterface provided. Registration Request invalid.")
		# 	continue
		installationParam = _grabPossibleEntry(request, "installationParam")
		installationParam = InstallationParam(
			_grabPossibleEntry(installationParam, "latitude"),
			_grabPossibleEntry(installationParam, "longitude"),
			_grabPossibleEntry(installationParam, "height"),
			_grabPossibleEntry(installationParam, "heightType"),
			_grabPossibleEntry(installationParam, "horizontalAccuracy"),
			_grabPossibleEntry(installationParam, "verticalAccuracy"),
			_grabPossibleEntry(installationParam, "indoorDeployment"),
			_grabPossibleEntry(installationParam, "antennaAzimuth"),
			_grabPossibleEntry(installationParam, "antennaDowntilt"),
			_grabPossibleEntry(installationParam, "antennaGain"),
			_grabPossibleEntry(installationParam, "eirpCapability"),
			_grabPossibleEntry(installationParam, "antennaBeamwidth"),
			_grabPossibleEntry(installationParam, "antennaModel")
		)
		# TODO: installationParam is condiitonal. Determine when it is needed.
		# if(not installationParam):
		# 	print("No installationParam provided. Registration Request invalid.")
		# 	continue
		measCapability = _grabPossibleEntry(request, "measCapability")
		# TODO: measCapability is conditional. Determine when it is required.
		# This may be "RECEIVED_POWER_WITH_GRANT" if a Node can RX while TX-ing
		# This may be "RECEIVED_POWER_WITHOUT_GRANT" if a Node will RX when not TX-ing
		# This may be empty ("") if the Node has no RX ability
		# This is an array, and a Node may be assigned both values (e.g. always RX)
		if(not measCapability):
			if("measCapability" in request): # An empty string ("") mean no RX capability. Do not cause error.
				measCapability = ""
			else:
				print("No measCapability provided. Registration Request invalid.")
				continue
		groupingParams = []
		groupingParam = _grabPossibleEntry(request, "groupingParam")
		for group in groupingParam:
			groupingParams.append(GroupParam(
				_grabPossibleEntry(group, "grouptype"),
				_grabPossibleEntry(group, "groupId")
			))

		cpiSignatureData = _grabPossibleEntry(request, "cpiSignatureData")
		cpiSignatureData = CpiSignatureData(
			_grabPossibleEntry(cpiSignatureData, "protectedHeader"),
			_grabPossibleEntry(cpiSignatureData, "encodedCpiSignedData"),
			_grabPossibleEntry(cpiSignatureData, "digitalSignature")
		)
		
		# TODO: Convert into VTParams Object
		vtParams = _grabPossibleEntry(request, "vtParams")

		nodes_awaiting_response.append(node)
		arr.append(RegistrationRequest(userId, fccId, 
			cbsdSerialNumber, callSign, cbsdCategory,
			cbsdInfo, airInterface, installationParam, 
			measCapability, groupingParams, cpiSignatureData, vtParams).asdict())
	return arr		

def configRegistrationReq():
	"""
	TODO - Craete a method that allows a user to pull a predefined JSON request from a file.

	Motivaition for this is to allow the hands on command line interface without the tedious form filling.
	"""
	return [None]

def cmdRegistrationReq():
	"""
	Provides Command Line Prompts for a user to create Registration Request(s)
 
	Note: UHD Lib provides the serial, addr, and model ('type' for the uhd lib) for all usrps. Nodes with an FPGA includes the fpga.
	Some 'type' matches with their 'product'. If there is a 'product', it is the same as the 'type' (e.g. x300).
	When 'product' doesn't exist, it seems to be of type 'usrp2' 

	TODO Change from "How many ..." to "Do you wanna do another?" && Is type USRP model?
	"""
	arr = []
	global nodes_awaiting_response
	nodes_awaiting_response = []
	num = promptNumOfRequests("How many Registration Requests would you like to create at this moment?: ")
	for _ in range(num):
		userId = input("Enter User ID: ")
		fccId = input("Enter FCC ID: ")
		cbsdSerialNumber = promptCbsdSerial(created_nodes) # TODO: Redo this so that array holds node
		nodes_awaiting_response.append(cbsdSerialNumber)
		callSign = input("Enter Call Sign (Optional - Press Enter to Skip): ")
		cbsdCategory = promptCbsdCategory()
		cbsdInfo = promptCbsdInfo(cbsdSerialNumber, created_nodes)
		airInterface = promptAirInterface()
		installationParam = None
		installationInfoSelector = getSelectorBoolean(input("Do you want to enter Device Installation Information (Y)es or (N)o: "))
		if(installationInfoSelector):
			installationParam = promptInstallationParam()
		measCapability = promptMeasCapability()
		groupingParam = None
		groupingParamSelector = getSelectorBoolean(input("Would you like to enter Grouping Parameter Info? (Y)es or (N)o: "))
		if(groupingParamSelector):
			quantity = int(input("How many groups do you want to create for this node?: ")) # TODO: Ensure non-negative (can this be 0?)
			for num in range(quantity):
				print("Node " + (num+1) + ":")
				print("Allowed Group Types: INTERFERENCE_COORDINATION. Select a combination below:")
				print("1. INTERFERENCE_COORDINATION")
				groupType = input("Selection: ")
				groupId = input("Enter Group ID: ") #** Do I add namespace after user input?
				groupingParam = [GroupParam(groupType, groupId)]
		arr.append(RegistrationRequest(userId, fccId, 
			cbsdSerialNumber, callSign, cbsdCategory,
			cbsdInfo, airInterface, installationParam, 
			measCapability, groupingParam, cpiSignatureData=None).asdict())
	return arr

def registrationRequest(clientio, payload=None):
	"""
	Function that should always be called for a Registration Request

	Parameters
	----------
	clientio : socket Object
		Socket connection to the SAS
	payload : array of Request(s) data
		Only used if the sim file is calling this funciton
	"""

	if(__sim_mode):
		arrOfRequest = simRegistrationReq(payload)
	else:
		while(True):
			user_input = input("Would you like to manually enter the registraion info or load from a file? (E)nter or (L)oad or (exit): ")
			if(user_input == 'E' or user_input == 'e'):
				arrOfRequest = cmdRegistrationReq() # Prompt User
				break
			elif(user_input == 'L' or user_input == 'l'):
				arrOfRequest = configRegistrationReq() # load config file
				break
			elif(user_input == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")
	
	payload = {"registrationRequest": arrOfRequest}
	clientio.emit("registrationRequest", json.dumps(payload))

def handleRegistrationResponse(clientio, data):
	"""
	Receives data from SAS after a Registration Request is made

	TODO: If SAS doesnt give all required info, then ignore the fact that we sent a request

	Parameters
	----------
	clientio : socketio Object
		Socket connection
	data : JSON string
		Registration response data
	"""
	json_data = json.loads(data)
	if(not (regResponses := _grabPossibleEntry(json_data, "registrationResponse"))):
		print("SASError: Unreadable data. Expecting JSON formatted payload. Registration invalid.")
		return
	print("\nRegistration Response(s) Received")
	iter = 0
	for regResponse in regResponses:
		print("Registration Response [" + str(iter := iter+1) + "]:")
		print(regResponse)

		if(not (cbsdId := _grabPossibleEntry(regResponse, "cbsdId"))):
			print("SASError: No cbsdId provided. Registration Response invalid.")
			continue
		
		# SAS should send responses in order, so popping from index[0] every time will give the proper Node
		if(node := nodes_awaiting_response.pop(0)):
			node.setCbsdId(cbsdId)
			print("Node with IP Address: '" + node.getIpAddress() +"' is given CBSD ID# : '" + cbsdId +"'.")
		else:
			print("No Node awaiting a response. Registration Response invalid.")
			continue
			
		if(not _hasResponseCode(regResponse)):
			print("No valid Response object found. Registration invalid.")
			continue
		
		if(measReportConfig := _grabPossibleEntry(regResponse, "measReportConfig")):
			if(not isinstance(measReportConfig, list)):
				measReportConfig = [measReportConfig]
			node.setMeasReportConfig(measReportConfig)

		# global registered_nodes #TODO This may not be required since I am using .append()
		registered_nodes.append(node)
		node.setRegistrationStatus(True)
		# TODO Update RX USRP with these params
# End Registation ------------------------------------------------------------------

# Spectrum Inquiry ----------------------------------------------------------------
def simSpectrumInquiryReq(requests):
	"""
	Simulation file provides info on what spectum info to request from SAS

	Parameters
	----------
	requests : array of dictionaries
		Spectrum Inquiry Request data
	"""
	arr = []
	iter = 0
	for request in requests:
		print("\nCreating Spectrum Inquiry Request [" + str(iter := iter+1) + "]:")
		print(request)

		if(not (node := reqAddressToNode(request))):
			print("Spectrum Inquiry Request invalid.")
			continue
		if(not (cbsdId := node.getCbsdId())):
			print("No cbsdId found for the node with IP Address: '" + node.getIpAddress() + "'. Spectrum Inquiry Request invalid.")
			continue
		inquiredSpectrum = []
		freqRanges = _grabPossibleEntry(request, "inquiredSpectrum")
		for freqRange in freqRanges:
			inquiredSpectrum.append(FrequencyRange(
				_grabPossibleEntry(freqRange, "lowFreq"),
				_grabPossibleEntry(freqRange, "highFreq")
			))

		measReport = _compileMeasReport(node)
		# TODO: measReport is required before a Node makes its first Grant request
		# Possibly ensure that if this is the first Spectrum Inquiry, that it includes measReport
		nodes_awaiting_response.append(node)
		arr.append(SpectrumInquiryRequest(cbsdId, inquiredSpectrum, measReport).asdict())
	return arr

def configSpectrumInquiryReq():
	"""
	TODO
	"""
	return [None]

def cmdSpectrumInquiryReq():
	"""
	Creates a Spectrum Inquiry Requests via command line input and returns a Spectrum Inquiry Request object
	"""
	arr = []
	# Print registered nodes' CBSD ID's
	print("Registered CBSD IDs:")
	for node in registered_nodes:
		print("\t"+node.get_CbsdId())
	cbsdId = input("Enter CBSD of node you want to use for the inquiry: ")
	inquiredSpectrum = promptFrequencyRange()
	provideRcvdPowerMeas = getSelectorBoolean(input("Do you want to provide Received Power Measurments to the SAS? (Y)es or (N)o: "))
	measReport = None
	if(provideRcvdPowerMeas):
		rcvdReport = promptRcvdPowerMeasReport()
		measReport = MeasReport([rcvdReport])
	arr.append(SpectrumInquiryRequest(cbsdId, inquiredSpectrum, measReport).asdict())
	return arr

def spectrumInquiryRequest(clientio, payload=None):
	"""
	Sends Spectrum Inquiry Request to the SAS
	"""
	if(__sim_mode):
		arrOfRequest = simSpectrumInquiryReq(payload)
	else:
		while(True):
			dataSource = input("Would you like to manually enter the Spectrum Inquiry Request info or load from a file? (E)nter or (L)oad: ")
			if(dataSource == 'E' or dataSource == 'e'):
				arrOfRequest = cmdSpectrumInquiryReq() # Prompt User
				break
			elif(dataSource == 'L' or dataSource == 'l'):
				arrOfRequest = configSpectrumInquiryReq() # load config file
				break
			elif(dataSource == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")
	payload = {"spectrumInquiryRequest": arrOfRequest}
	clientio.emit("spectrumInquiryRequest", json.dumps(payload))

def handleSpectrumInquiryResponse(clientio, data):
	"""
	Handles Spectrum Inquiry response(s) from the SAS
	
	TODO: Do something with this data. 
	"""
	jsonData = json.loads(data)
	iter = 0
	siResponses = _grabPossibleEntry(jsonData, "spectrumInquiryResponse")
	if(not siResponses):
		print("Unreadable data. Expecting JSON formatted payload. Spectrum Inquiry Response(s) invalid.")
		return
	print("Spectrum Inquiry Response Received")
	for SIResponse in siResponses:
		print("Spectrum Inquiry Response [" + str(iter := iter+1) +"]:")
		print(SIResponse)

		if(cbsdId := _grabPossibleEntry(SIResponse, "cbsdId")):
			node = findNodeAwaitingResponseByCbsdId(cbsdId)
			if(not node):
				print("No Node awaiting a response has the cbsdId '" + cbsdId +"'. Spectrum Inquiry Response invalid.")
				continue
			nodes_awaiting_response.remove(node) # Remove node from waiting list
		else:
			print("No cbsdId provided. Spectrum Inquiry Response invalid.")
			continue

		if(not (responseCode := _hasResponseCode(SIResponse))):
			print("Spectrum Inquiry invalid.")
			continue

		if(availableChannel := _grabPossibleEntry(SIResponse, "availableChannel")):
			if(not (frequencyRange := _grabPossibleEntry(SIResponse, "frequencyRange"))):
				print("Required parameter frequencyRange not found. Spectrum Inquiry Response invalid.")
				continue
			channelType = _grabPossibleEntry(SIResponse, "channelType")
			if(not channelType):
				print("Required parameter channelType not found. Spectrum Inquiry Response invalid.")
				continue
			ruleApplied = _grabPossibleEntry(SIResponse, "ruleApplied")
			if(not ruleApplied):
				print("Required parameter ruleApplied not found. Spectrum Inquiry Response invalid.")
				continue
			maxEirp = _grabPossibleEntry(SIResponse, "maxEirp")
		else:
			print("No availableChannel found.")
		
		# TODO: Do  something with all this information
# End Spectrum Inquiry ------------------------------------------------------------

# Grant ---------------------------------------------------------------------------
def simGrantReq(requests):
	"""
	Function for simulation file to create a Grant request

	Parameters
	----------
	requests : array of dictionaries
		Grant Request data
	"""
	arr = []
	iter = 0
	for request in requests:
		print("\nCreating Grant Request [" + str(iter := iter+1) + "]:")
		print(request)

		if(not (node := reqAddressToNode(request))):
			print("Grant Request invalid.")
			continue
		if(not (cbsdId := node.getCbsdId())):
			print("No cbsdId found for the node with IP Address: '" + node.getIpAddress() + "'. Grant Request invalid.")
			continue

		measReport = _grabPossibleEntry(request, "measReport")

		operationParam = _grabPossibleEntry(request, "operationParam")
		if(not operationParam):
			print("No operationParam found. Grant Request invalid.")
			continue
		freqRange = _grabPossibleEntry(operationParam, "operationFrequencyRange")
		operationParam = OperationParam(
				_grabPossibleEntry(operationParam, "maxEirp"),
				 FrequencyRange(
				 		lowFreq := _grabPossibleEntry(freqRange, "lowFrequency"),
				 		highFreq := _grabPossibleEntry(freqRange, "highFrequency")
				 	)
			)

		# Update the USRP with the proposed Operation Parameters in anticiaption of a sucessful grant request
		bandwidth = int(highFreq) - int(lowFreq)
		cFreq = int(lowFreq) + (bandwidth/2)
		# TODO: Update output power
		node.updateTxParams(fc=cFreq, bw=bandwidth)
		
		# Read VTGrantParams from JSON and create object
		vtGrantParams = _grabPossibleEntry(request, "vtGrantParams")
		if(vtGrantParams):
			(minFrequency, maxFrequency, preferredFrequency, frequencyAbsolute, 
			minBandwidth, maxBandwidth, preferredBandwidth, startTime, 
			endTime, approximateByteSize, dataType, powerLevel, 
			location, mobility, maxVelocity) = unpackResponseWithKeys(
				vtGrantParams, "minFrequency", "maxFrequency", "preferredFrequency", "frequencyAbsolute", 
				"minBandwidth", "maxBandwidth", "preferredBandwidth", "startTime", 
				"endTime", "approximateByteSize", "dataType", "powerLevel", 
				"location", "mobility", "maxVelocity")
			vtGrantParams = VTGrantParams(minFrequency, maxFrequency, preferredFrequency, frequencyAbsolute, 
			minBandwidth, maxBandwidth, preferredBandwidth, startTime, 
			endTime, approximateByteSize, dataType, powerLevel, 
			location, mobility, maxVelocity)
		
		nodes_awaiting_response.append(node) # Add Node to list of Nodes waiting for SAS Acknowledgment 
		arr.append(GrantRequest(cbsdId, operationParam, measReport, vtGrantParams).asdict())
	return arr

def configGrantReq():
	"""
	TODO
	"""
	return [None]

def cmdGrantReq():
	"""
	Creates a Grant Request from command line information and request send to SAS
	"""
	arr = []
	# Print registered nodes' CBSD ID's
	print("Registered CBSD IDs:")
	for node in registered_nodes:
		print("\t"+node.get_CbsdId())
		cbsdId = input("Enter CBSD of node you want to use for the grant request: ")
		operationParam = promptOperationParam()
		measReport = None
		provideRcvdPowerMeas = getSelectorBoolean(input("Do you want to provide Received Power Measurments to the SAS? (Y)es or (N)o: "))
		if(provideRcvdPowerMeas):
			rcvdReport = promptRcvdPowerMeasReport()
			measReport = MeasReport([rcvdReport])
		vtGrantParams = None
		provideVtGrantParams = getSelectorBoolean(input("Do you want to provide VT Grant Params? (Y)es or (N)o: "))
		if(provideVtGrantParams):
			vtGrantParams = promptVtGrantParams()
		arr.append(GrantRequest(cbsdId, operationParam, measReport, vtGrantParams).asdict())
	return arr

def grantRequest(clientio, payload=None):
	"""
	Creates a Grant Request and sends it to the SAS
	"""
	arrOfRequest = None
	if(__sim_mode):
		arrOfRequest = simGrantReq(payload)
	else:
		while(dataSource := input("Would you like to manually enter the Grant Request info or load from a file? (E)nter or (L)oad: ")):
			if(dataSource == 'E' or dataSource == 'e'):
				arrOfRequest = cmdGrantReq()
				break
			elif(dataSource == 'L' or dataSource == 'l'):
				arrOfRequest = configGrantReq()
				break
			elif(dataSource == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")
	payload = {"grantRequest": arrOfRequest}
	clientio.emit("grantRequest", json.dumps(payload))

def handleGrantResponse(clientio, data):
	"""
	Handles Grant Response message from SAS to CBSD.
	TODO: No 1st heartbeatRequest is automatically launched, so the user must manually do so.
	This is for flexiblity in when a grant is requested and when the heartbeats begin.
	Maybe a grant is for next year, so there is no need for a heartbeat now, hence why this is as it is.
	"""
	jsonData = json.loads(data)
	if(not (grantResponses := _grabPossibleEntry(jsonData, "grantResponse"))):
		print("Unreadable data. Expecting JSON formatted payload. Grant(s) invalid.")
		return
	print("\nGrant Response(s) Received")
	iter = 0
	for grantResponse in grantResponses:
		print("Grant Response [" + str(iter := iter+1) +"]:")
		print(grantResponse)

		# Step 1: Check to see what Node this response belongs to
		if(cbsdId := _grabPossibleEntry(grantResponse, "cbsdId")):
			if(not (node := findNodeAwaitingResponseByCbsdId(cbsdId))):
				print("No Node awaiting a response has the cbsdId '" + cbsdId + "'. Grant Response invalid.")
				continue
		else:
			print("SASError: No cbsdId provided. Grant Response invalid.")
			continue
	
		# Step 2: Remove the Node from the waiting list
		nodes_awaiting_response.remove(node)
		
		# Step 3: Get the Response Code
		if((responseCode := _hasResponseCode(grantResponse))):
			if(responseCode != "0"):
				# TODO: If SAS provides Operation Parameters, decided if the Node
				# should re-send a new Grant request with the parameters or not
				# if(operationParam := _grabPossibleEntry(grantResponse, "operationParam")):
				# 	pass
				print("Response Code does not indicate successful grant request. Grant Response invalid.")
				continue
		else:
			print("Grant Response invalid.")
			continue

		# Step 4: Get rest of data
		if(not (channelType := _grabPossibleEntry(grantResponse, "channelType"))):
			print("SASError: No channelType provided. Grant invalid.")
			continue
		if(not (grantId := _grabPossibleEntry(grantResponse, "grantId"))):
			print("SASError: No grantId provided. Grant invalid")
			continue			
		if((grantExpireTime := _grabPossibleEntry(grantResponse, "grantExpireTime"))):
			timeFormat = "%Y%m%dT%H:%M:%S%Z"
			try:
				expireDateTime = datetime.strptime(grantExpireTime, timeFormat)
			except ValueError:
				print("SASError: SAS sent grantExpireTime as '"+str(grantExpireTime)+"' which is not in "+timeFormat+" format. Grant invalid.")
				continue
		else:
			print("SASError: No grantExpireTime provided. Grant invalid.")
			continue
		
		if(not (heartbeatInterval := _grabPossibleEntry(grantResponse, "heartbeatInterval"))):
			print("SASError: No heartbeatInterval provided. Grant invalid.")
			continue

		# TODO: Ensure the measReportConfigs are valid strings as per the WinnForum specs
		if(measReportConfig := _grabPossibleEntry(grantResponse, "measReportConfig")):
			if(not isinstance(measReportConfig, list)):
				measReportConfig = [measReportConfig]
			node.setMeasReportConfig(measReportConfig)

		# Step 5: Create Grant object for Node
		node.setGrant(grantId, "GRANTED", expireDateTime, heartbeatInterval, channelType)
# End Grant ------------------------------------------------------------------------

# Heartbeat ------------------------------------------------------------------------
def scheduleNextHeartbeat(clientio, node):
	"""
	Helper function that schedules a Heartbeat Request for a CBSD/Node

	Parameters
	----------
	clientio : socket Object
		Socket to SAS
	node : Node object
		Node that will be making the heartbeat request
	"""
	delayTilNextHeartbeat = float(node.getGrant().getHeartbeatInterval()) * 0.9 # Send heartbeats a little sooner than the interval
	if(delayTilNextHeartbeat < 1):
		delayTilNextHeartbeat = 1
	threading.Timer(delayTilNextHeartbeat, heartbeatRequest, [clientio, node]).start()

def repeatHeartbeatRequest(node):
	"""
	This is called when a threaded heartbeat request creates a Heartbeat Request.
	The Thread calls heartbeatRequest() with a node parameter indicating that it is not the first heartbeat.

	Parameters
	----------
	node : Node object
		Node that is making a heartbeat request
	"""
	grantStatus = node.getGrant().getGrantStatus()
	if(grantStatus == "IDLE"):
		return None
	cbsdId = node.getCbsdId()
	grantId = node.getGrant().getGrantId()
	grantRenew = False # TODO: Properly implement this feature
	operationState = node.getGrant().getGrantStatus()
	measReport = _compileMeasReport(node)
	nodes_awaiting_response.append(node)
	return [HeartbeatRequest(cbsdId, grantId, grantRenew, operationState, measReport).asdict()]

def simHeartbeatReq(requests):
	"""
	The simulation file should only kick off the very first heartbeat for a grant.
	The rest of the heartbeats are to be automated.

	TODO
	"""
	arr = []
	iter = 0
	for request in requests:
		print("\nCreating Heartbeat Request [" + str(iter := iter+1) + "]:")
		print(request)

		if(not (node := reqAddressToNode(request))):
			print("Heartbeat Request invalid.")
			continue
		if(not (cbsdId := node.getCbsdId())):
			print("No cbsdId found for the node with IP Address: '" + node.getIpAddress() + "'. Heartbeat Request invalid.")
			continue
		if(not (grantId := node.getGrant().getGrantId())):
			print("No grantId found for the node with cbsdId: '" + cbsdId + "'. Heartbeat Request invalid.")
			continue
		operationState = node.getGrant().getGrantStatus()
		measReport = _compileMeasReport(node)
		nodes_awaiting_response.append(node)
		arr.append(HeartbeatRequest(cbsdId, grantId, operationState=operationState, 
		measReport=measReport).asdict())
	return arr

def configHeartbeatReq():
	"""
	TODO
	"""
	return [None]

def cmdHeartbeatReq():
	"""
	Prompts user through creating a Heartbeat request.
	This should only kick off the very first heartbeat.
	The rest of the heartbeats are to be automated.

	TODO: Add user option to fill multiple requests out
	"""
	arr = []
	cbsd = None
	# Print registered nodes' CBSD ID's
	print("Registered CBSD IDs:")
	for node in registered_nodes:
		print("\t"+node.get_CbsdId())
	cbsdId = input("Enter CBSD ID of node you want to use for the heartbeat request: ")
	for cbsd in registered_nodes:
		if(cbsd.get_CbsdId() == cbsdId):
			node = cbsd
	grantId = node.get_GrantId() # TODO: error handle this
	grantRenew = getSelectorBoolean(input("Would you like to renew the grant? (Y)es or (N)o: "))
	operationState = node.getGrant().getGrantStatus()
	measReport = None
	provideRcvdPowerMeas = getSelectorBoolean(input("Do you want to provide Received Power Measurments to the SAS? (Y)es or (N)o: "))
	if(provideRcvdPowerMeas):
		rcvdReport = promptRcvdPowerMeasReport()
		measReport = MeasReport([rcvdReport])
	nodes_awaiting_response.append(node)
	arr.append(HeartbeatRequest(cbsdId, grantId, grantRenew, operationState, measReport).asdict())
	return arr

def heartbeatRequest(clientio, node=None, payload=None):
	"""
	Function is always called to create a Heartbeat Request.

	This function is automatically scheduled after a Heartbeat Response.

	Parameters
	----------
	clientio : socket Object (required)
		SAS socket connection.
	payload : dictonary (conditional)
		Dictonary of data used by simulation file to create hb request.
		Only included if Simulation file is kicking off the first heartbeat for a Grant.
	node : Node Object (conditional)
		Node that is actively sending Heartbeats.
		Only included if the heartbeat is NOT the first one for a Grant.
	"""
	if(payload):
		arrOfRequest = simHeartbeatReq(payload)
	elif(node):
		arrOfRequest = repeatHeartbeatRequest(node)
	else:
		while(dataSource := input("Would you like to manually enter the Heartbeat Request info or load from a file? (E)nter or (L)oad: ")):
			if(dataSource == 'E' or dataSource == 'e'):
				arrOfRequest = cmdHeartbeatReq()
				break
			elif(dataSource == 'L' or dataSource == 'l'):
				arrOfRequest = configHeartbeatReq()
				break
			elif(dataSource == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")

	if(arrOfRequest):
		payload = {"heartbeatRequest": arrOfRequest}
		clientio.emit("heartbeatRequest", json.dumps(payload))

		# Start timer to track how long it takes for each response to come in 
		timeTilHearbeatExpires = 240 # seconds #TODO Should be heartbeatInterval
		for hbReq in arrOfRequest:
			for node in registered_nodes:
				if(node.getCbsdId() == hbReq["cbsdId"]):
					node.startHbTimer(timeTilHearbeatExpires)
					break

def handleHeartbeatResponse(clientio, data):
	"""
	Handles Heartbeat Response message from SAS to CBSD

	TODO: This assumes every Node can only have 1 Grant. 
	Changes must be made here to accommodate multiple Grants per Node.
	"""
	jsonData = json.loads(data)
	if(not (hbResponses := _grabPossibleEntry(jsonData, "heartbeatResponse"))):
		print("SASError: Unreadable data. Expecting JSON formatted payload. Heartbeat(s) invalid.")
		return
	print("\nHeartbeat Response(s) Received")
	iter = 0
	for hbResponse in hbResponses:
		isIncompleteResponse = False
		print("Heartbeat Response [" + str(iter := iter+1) +"]:")
		print(hbResponse)
	
		# Unpack Heartbeat Response data
		(cbsdId, grantId, transmitExpireTime, grantExpireTime,
		heartbeatInterval, measReportConfig, responseCode) = unpackResponseWithKeys(
			hbResponse,  "cbsdId", "grantId", "transmitExpireTime", "grantExpireTime", 
		"heartbeatInterval", "measReportConfig", "responseCode")

		# Check for a Node with the cbsdId+grantId the SAS sent in the response
		if(cbsdId): 
			if((node := findNodeAwaitingResponseByCbsdId(cbsdId))): # Find the Node with the given CBSD ID
				node.stopHbTimer() # TODO: For MultipleGrants - Should this be stopped when the grantId is matched or just the Node?
				nodes_awaiting_response.remove(node)
				if(grantId):
					if(not (node.getGrant().getGrantId() == grantId)):  # Find if the Node has a Grant with the given Grant ID
						print("This Node with CBSD ID: '" + cbsdId + "' does not have a Grant with Grant ID: '" + grantId + "'.")
						isIncompleteResponse = True
				else:
					if(responseCode == "0"):
						print("SASError: Missing required parameter: grantId. Cannot match this response to a Grant without a Grant ID.")
					else:
						print("Missing conditional parameter: grantId. Cannot match this response to a Grant without a Grant ID.")
					isIncompleteResponse = True
			else:
				print("No Node awaiting a response has the cbsdId '" + cbsdId +"'.")
				isIncompleteResponse = True
		else:
			print("Missing conditional parameter: cbsdId. Cannot match this response to any Node without a CBSD ID.")
			isIncompleteResponse = True
		
		if(transmitExpireTime):
			pass # TODO: import datetime and do math
			# Take transmitExpireTime and subtract current time from it
			# txExpiration = transmitExpireTime - currentTime
			# With the time difference, start a delayed thread that turns off tx
			# threading.Timer(txExpiration, node.disableTx())
		else:
			print("SASError: Missing required parameter: transmitExpireTime.")
			isIncompleteResponse = True

		# TODO: grantExpireTime is required when (responseCode is 0 or 501) and (the heartbeat request asked to renew the Grant)
		# Must find out how to determine is a Node asked to renew at this point
		if(grantExpireTime):
			node.getGrant().setGrantExpireTime(grantExpireTime)

		if(measReportConfig):
			if(not isinstance(measReportConfig, list)):
				measReportConfig = [measReportConfig]
			node.setMeasReportConfig(measReportConfig)
		if(heartbeatInterval):
			node.getGrant().setHeartbeatInterval(heartbeatInterval)
		
		# TODO: If SAS provides Operation Parameters, decide if the Node
		# should re-send a new Grant request with the parameters or not
		# if(operationParam := _grabPossibleEntry(grantResponse, "operationParam")):
		# 	pass
		
		# Determine what action to take with the information provided
		if(isIncompleteResponse): # Terminate Grant if SAS did not send a completely valid Response
			node.changeGrantStatus("IDLE") 
			print("SAS Heartbeat Response Invalid. Terminating Grant.")
		elif(responseCode == "500"): 	# 500 --> TERMINATED_GRANT
			node.changeGrantStatus("IDLE") 
			print("SAS indicates terminated Grant. Terminating Grant.")
		elif(responseCode == "501"):	# 501 --> SUSPENDED_GRANT
			node.changeGrantStatus("GRANTED")
			print("SAS indicates suspended Grant. Suspending Grant.")
			scheduleNextHeartbeat(clientio, node)
		elif(responseCode == "502"):	# 502 --> UNSYNC_OP_PARAM
			node.changeGrantStatus("IDLE")
			print("SAS indicates that Grant state is out of sync with the CBSD. Terminating Grant.")
		elif(responseCode == "0"):		# 0   --> SUCCESS
			if(node.getGrant().getGrantStatus() == "GRANTED"):
				node.changeGrantStatus("AUTHORIZED")
			scheduleNextHeartbeat(clientio, node)
# End Heartbeat --------------------------------------------------------------------

# Relinquishment -------------------------------------------------------------------
def simRelinquishmentReq(requests):
	"""
	Read sim file for Relinquishment Request(s)
	"""
	arr = []
	iter = 0
	for request in requests:
		print("\nCreating Relinquishment Request [" + str(iter := iter+1) + "]:")
		print(request)
		node = reqAddressToNode(request)
		if(not node):
			print("No Registered Node was found with the IP Address: '" + node.getIpAddress() + "'. Relinquishment Request invalid.")
			continue
		cbsdId = node.getCbsdId()
		if(not cbsdId):
			print("No cbsdId found for the node with IP Address: '" + node.getIpAddress() + "'. Relinquishment Request invalid.")
			continue
		grantId = node.getGrant().getGrantId()
		nodes_awaiting_response.append(node)
		arr.append(RelinquishmentRequest(cbsdId, grantId).asdict())
	return arr

def configRelinquishmentReq():
	"""
	TODO
	"""
	return [None]		

def cmdRelinquishmentReq():
	"""
	Creates a Relinquishment Request and sends it to the SAS 
	"""
	arr = None
	cbsd = None
	# Print registered nodes' CBSD ID's
	print("Registered CBSD IDs:")
	for node in registered_nodes:
		print("\t"+node.get_CbsdId())
	cbsdId = input("Enter CBSD of node you want to use for the grant request: ")
	for node in registered_nodes:
		if(node.get_CbsdId() == cbsdId):
			cbsd = node
	grantId = cbsd.get_GrantId() # TODO: error handle this
	arr.append(RelinquishmentRequest(cbsdId, grantId).asdict())
	return arr

def relinquishmentRequest(clientio, payload=None):
	"""
	Creates Relinishment Request to send to the SAS
	"""
	arrOfRequest = None
	if(__sim_mode):
		arrOfRequest = simRelinquishmentReq(payload)
	else:
		while(dataSource := input("Would you like to manually enter the Relinquishment Request info or load from a file? (E)nter or (L)oad: ")):
			if(dataSource == 'E' or dataSource == 'e'):
				arrOfRequest = cmdRelinquishmentReq()
				break
			elif(dataSource == 'L' or dataSource == 'l'):
				arrOfRequest = configRelinquishmentReq()
				break
			elif(dataSource == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")
	payload = {"relinquishmentRequest": arrOfRequest}
	clientio.emit("relinquishmentRequest", json.dumps(payload))

def handleRelinquishmentResponse(clientio, data):
	"""
	Handles data returned from SAS regarding previously sent Relinquishment Request.

	Relinquishment Requests resets the Grant object for a Node
	"""
	jsonData = json.loads(data)
	if(not (relinquishResponses := _grabPossibleEntry(jsonData, "relinquishmentResponse"))):
		print("Unreadable data. Expecting JSON formatted payload with key 'relinquishmentResponse'. Relinquishment(s) invalid.")
		return
	print("\nRelinquishment Response(s) Received")
	iter = 0
	for relinquishment in relinquishResponses:
		print("Relinquishment Response [" + str(iter := iter+1) +"]:")
		print(relinquishment)

		(cbsdId, grantId, responseCode) = unpackResponseWithKeys(relinquishment, "cbsdId", "grantId", "responseCode")
		isIncompleteResponse = False
		if(cbsdId):
			if(node := findNodeAwaitingResponseByCbsdId(cbsdId)):
				if(grantId):
					if(not (node.getGrant().getGrantId() == grantId)):  # Find if the Node has a Grant with the given Grant ID
						print("This Node with CBSD ID: '" + cbsdId + "' does not have a Grant with Grant ID: '" + grantId + "'.")
						isIncompleteResponse = True
				else:
					if(responseCode == "0"):
						print("Missing required parameter: grantId. Cannot match this response to a Grant without a Grant ID.")
					else:
						print("Missing conditional parameter: grantId. Cannot match this response to a Grant without a Grant ID.")
					isIncompleteResponse = True					
			else:
				print("No Node awaiting a response has the cbsdId '" + cbsdId +"'. Relinquishment invalid.")
				isIncompleteResponse = True					
		else:
			print("Missing conditional parameter: cbsdId. Cannot match this response to any Node without a CBSD ID.")
			isIncompleteResponse = True	
		
		if(isIncompleteResponse): 
			print("SAS Relinquishment Response Invalid. Grant Remains Active.")
		elif(responseCode == "0"):
			node.changeGrantStatus("IDLE")
			print("Grant Relinquished.")
# End Relinquishment ---------------------------------------------------------------

# Deregistration -------------------------------------------------------------------
def simDeregistrationReq(requests):
	"""
	Read sim file for Deregistration Request(s)
	"""
	arr = []
	global nodes_awaiting_response
	nodes_awaiting_response = []
	iter = 0
	for request in requests:
		print("\nCreating Deregistration Request [" + str(iter := iter+1) + "]:")
		print(request)
		node = reqAddressToNode(request)
		if(not node):
			print("No Created Node was found with the IP Address: '" + node.getIpAddress() + "'. Deregistration Request invalid.")
			continue
		cbsdId = node.getCbsdId()
		if(not cbsdId):
			print("No cbsdId found for the node with IP Address: '" + node.getIpAddress() + "'. Deregistration Request invalid.")
			continue
		nodes_awaiting_response.append(node)
		arr.append(DeregistrationRequest(cbsdId).asdict())
	return arr

def configDeregistrationReq():
	"""
	TODO
	"""
	return [None]

def cmdDeregistrationReq():
	"""
	Prompts user through creating a deregistration request
	"""
	arr = None
	cbsd = None
	# Print registered nodes' CBSD ID's
	print("Registered CBSD IDs:")
	for node in registered_nodes:
		print("\t"+node.get_CbsdId())
	cbsdId = input("Enter CBSD of node you want to use for the deregistration request: ")
	arr.append(DeregistrationRequest(cbsdId).asdict())
	return arr

def deregistrationRequest(clientio, payload=None):
	"""
	Creates a Deregistration request and sends it to the SAS
	"""
	if(__sim_mode):
		arrOfRequest = simDeregistrationReq(payload)
	else:
		while(dataSource := input("Would you like to manually enter the Deregistration Request info or load from a file? (E)nter or (L)oad: ")):
			if(dataSource == 'E' or dataSource == 'e'):
				arrOfRequest = cmdDeregistrationReq()
				break
			elif(dataSource == 'L' or dataSource == 'l'):
				arrOfRequest = configDeregistrationReq()
				break
			elif(dataSource == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")
	payload = {"deregistrationRequest": arrOfRequest}
	clientio.emit("deregistrationRequest", json.dumps(payload))

def handleDeregistrationResponse(clientio, data):
	"""
	Handles SAS Deregistration Response sent to CBSD
	Deletes deregistered Node from created_nodes
	"""
	jsonData = json.loads(data)
	if(not (deregistrationResponses := _grabPossibleEntry(jsonData, "deregistrationResponse"))):
		print("Unreadable data. Expecting JSON formatted payload with key 'deregistrationResponse'. Deregistration(s) invalid.")
		return
	iter = 0
	print("\nDeregistration Response(s) Received")
	for dereg in deregistrationResponses:
		print("Deregistration Response [" + str(iter := iter+1) +"]:")
		print(dereg)
		if(not (responseCode := _hasResponseCode(dereg))):
			print("Deregistration invalid.")
			continue
		if(not (cbsdId := _grabPossibleEntry(dereg, "cbsdId"))):
			print("No cbsdId provided. Deregistration invalid.")
			continue
		if(not (node := findNodeAwaitingResponseByCbsdId(cbsdId))):
			print("No Node awaiting a response has the cbsdId '" + cbsdId +"'. Deregistration invalid.")
			continue
		node.setRegistrationStatus(False)

		# TODO: If you Deregister, should you also delete the Node from created_nodes?
		node.getUsrp().stop()
		node.getUsrp().wait()
		global created_nodes
		created_nodes.remove(node)
# End Deregistration ---------------------------------------------------------------

# SAS Socket Events (Not WinnForum Specified) --------------------------------------
def spectrumData(cbsdId, clientio):
	"""
	Provide SAS with Spectrum Data by emitting "spectrumData"
	There is a presumption that the SAS is not askng for more than 10MHz from 1 node.

	Parameters
	----------
	cbsdId : string
		CBSD ID of the Node that is taking the measurments
	
	clientio : Socket object
		SAS Socket connection
	"""
	measReport = _compileMeasReport(findRegisteredNodeByCbsdId(cbsdId))
	payload = {"cbsdId":cbsdId, "spectrumData": measReport.asdict()}
	clientio.emit("spectrumData", json.dumps(payload))

def incumbentInformation(clientio, requests):
	"""This allows a node to register as a PU (research purposes)"""
	arr = []
	for request in requests: 
		if(not (node := reqAddressToNode(request, mustBeRegistered=False))):
			print("Incumbent Information Request invalid.")
			continue
		desireObfuscation = _grabPossibleEntry(request, "desireObfuscation")
		startTime = _grabPossibleEntry(request, "startTime")
		puLat = _grabPossibleEntry(request, "puLat")
		puLon = _grabPossibleEntry(request, "puLon")
		power = _grabPossibleEntry(request, "power")
		if(inquiredSpectrum := _grabPossibleEntry(request, "inquiredSpectrum")):
			lowFreq = _grabPossibleEntry(inquiredSpectrum, "lowFreq")
			highFreq = _grabPossibleEntry(inquiredSpectrum, "highFreq")
		arr.append()

	clientio.emit("incumbentInformation", json.dumps(payload))
def updateRxParams(data):
	"""
	Handles SAS Command to change RX Parameters

	Parameters
	----------
	data : dictonary
		Keys include cbsdId, lowFreq, and highFreq for RX Node
	"""
	print("SAS Emitted 'changeRadioParams' with data:")
	print(data)
	if(cbsdId := _grabPossibleEntry(data, "cbsdId")):
		if(node := findRegisteredNodeByCbsdId(cbsdId)):
			if(lowFreq := safeCast(_grabPossibleEntry(data,
                            "lowFrequency"), int) != None):
				if(highFreq :=
                                        safeCast(_grabPossibleEntry(data,
                                            "highFrequency"), int) != None):
					bw = (highFreq - lowFreq)
					fc =  highFreq - (bw / 2)
					node.updateRxParams(fc, bw)
				else:
					print("SAS Attempted 'updateRxParams' but no valid integer 'highFrequency' found. Ignoring SAS call.")
			else:
				print("SAS Attempted 'updateRxParams' but no valid integer 'lowFrequency' found. Ignoring SAS call.")
		else:
			print("SAS Attempted 'updateRxParams' but no registered Node found with cbsdId '" + cbsdId + "'. Ignoring SAS call.")
	else:
		print("SAS Attempted 'updateRxParams' but no cbsdId found. Ignoring SAS call.")

def emergencyStop(data):
	"""
	SAS sends 1 grantId at a time when a Node must turn off TX

	TODO: Get proper socket event name for this
	"""
	jsonData = json.loads(data)
	if(not (grantId :=_grabPossibleEntry(jsonData, "grantId"))):
		print("No grantId '" + grantId + "' found in emergency.")
	else:
		for node in registered_nodes:
			if(grantId == node.getGrant().getGrantId()):
				node.disableTx()
				break
# End SAS Socket Events (Not WinnForum Specified) ----------------------------------

def delayUntilTime(lastTime, currentTime):
	"""
	Used in main() by the simulation file, this uses the 'time' key and waits to execute the command at that time.

	Parameters
	----------
	lastTime : int
		The last key that resembles time
	currentTime : string
	"""
	try:
		currentTime = int(currentTime)
	except:
		print("Could not convert 'time' key into an integer.")
		return None
	time.sleep(currentTime - lastTime)
	return currentTime

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


def endClientExecution(clientio):
	"""
	Gracefully ends client execution by turning off all USRPs and exiting the program
	TODO: Ensure to end all Timed/Running threads as well
	"""
	for node in created_nodes:
		if(radio := node.getUsrp()):
			radio.stop()
			radio.wait()
	clientio.disconnect()

def init(args):
	"""
	Create radio object and connects to server

	Parameters
	----------
	args : list
		List of parameters extracted from command line flags
	"""

	clientio = socketio.Client()  # Create Client Socket
	defineSocketEvents(clientio)  # Define handlers for events the SAS may emit
	socket_addr = 'http://' + args['address'] +':' + args['port']
	clientio.connect(socket_addr) # Connect to SAS

	global __blocked
	__blocked = False
	if(args['sim']):
		'''
		Simulation file includes all requests to make and at what times
		This requires no human interaction with the program. There may be output to read in the terminal.
		'''
		global __sim_mode
		__sim_mode = True
		path = args['sim']
		try:
			with open(path) as config:
				data = json.load(config)
		except:
			sys.exit("Fatal Error: No valid simulation file found at "+str(path)+"\nExiting program...")
		lastTime = 0
		for timeToExecute in data: 				# Sim file may have multiple instances of time to trigger events
			lastTime = delayUntilTime(lastTime, timeToExecute)
			for action in data[timeToExecute]: 	# Each time may have multiple actions (requests)
				for func in action:				# Each requests may have multiple payloads
					funcStarted = False
					while(True):
						if(not __blocked):
							if(funcStarted):
								break
							print("\nGoing to execute: " + func, flush=True)
							payload = action[func]
							if(func == "createNode"):
								createNode(payload)
							elif(func == "registrationRequest"):
								__blocked = True
								registrationRequest(clientio, payload)
							elif(func == "spectrumInquiryRequest"):
								__blocked = True
								spectrumInquiryRequest(clientio, payload)
							elif(func == "grantRequest"):
								__blocked = True
								grantRequest(clientio, payload)
							elif(func == "heartbeatRequest"):
								__blocked = True
								heartbeatRequest(clientio, payload=payload)
							elif(func == "relinquishmentRequest"):
								__blocked = True
								relinquishmentRequest(clientio, payload)
							elif(func == "deregistrationRequest"):
								__blocked = True
								deregistrationRequest(clientio, payload)
							elif(func == "endSimulation"):
								print("Ending Simulation...")
								endClientExecution(clientio)
							elif(func == "incumbentInformation"):
								__blocked == True
								incumbentInformation(clientio, payload)
							funcStarted = True
	else:
		# Commandline (CMD) Interface Main Menu
		# CMD is blocking sockets from printing until user enters another value
		# To remedy this, I may add a boolean that is True when the socket is busy 
		# Once the socket is done completeing the action the user entered, the bool
		# should allow the loop to proceed... TODO
		cmdCreateNode()
		print("Enter 'h' for help/list of commands")
		while(True):
			while(not __blocked):
				userInput = input("User Input: ")
				if(userInput == 'h'):
					print("""Commands Include:
						0 - Exit SAS Interface
						1 - View Created Nodes
						2 - Create USRP Node
						3 - Create Registration Request
						4 - Create Spectrum Inquiry Request
						5 - Create Grant Request
						6 - Create Heartbeat Request
						7 - Create Relinquishment Request
						8 - Create Deregistration Request
						""")
				elif(userInput == '0'):
					if(promptSASDisconnect()):
						endClientExecution(clientio)
				elif(userInput == '1'):
					printNodeArray("created")
				elif(userInput == '2'):
					createNode()
				elif(userInput == '3'):
					__blocked = True
					registrationRequest(clientio)
				elif(userInput == '4'):
					__blocked = True
					spectrumInquiryRequest(clientio)
				elif(userInput == '5'):
					__blocked = True
					grantRequest(clientio)
				elif(userInput == '6'):
					__blocked = True
					heartbeatRequest(clientio)
				elif(userInput == '7'):
					__blocked = True
					relinquishmentRequest(clientio)
				elif(userInput == '8'):
					__blocked = True
					deregistrationRequest(clientio)
		
if __name__ == '__main__':
	args = vars(parser.parse_args())	# Get command line arguments
	init(args)							
	