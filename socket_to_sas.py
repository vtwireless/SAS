#!/usr/bin/env python3

# GNU Radio Python Flow Graph
# Title: SAS USRP Transmitter
# Author: Cam Makin
# For Research Efforts: Wireless@VT
# Description: Implementiation of an SDR Tx for SAS control. This flowgraph is the base of the TX Python script that will be further modified to include sockets and other SAS API requirements.
# GNU Radio version: 3.8.1.0
# Generated October 7, 2020
# Last Updated: 01/05/2021

# TODO: Dynamic Socket Addressing (Want to be able to switch address/port of socket on the fly)
# TODO: Decide how SAS assigned info (i.e. cbsdId) is stored
# TODO: Create some command line keyword that works at all instances to exit from the prompt...
# TODO: Create a function to handle the "response" field from all the SAS responses
# TODO: Maybe add menu option to view all history to see what has been done and their responses
#./socket_tx.py -p 5000 -a "127.0.0.1"


import sys
from argparse import ArgumentParser
from gnuradio import uhd
import socketio
import json
from usrps import tx_usrp # TX Usrp object 
from WinnForum import *		# File containing object definitions used
from cmd_prompts import * 	# User defined library for cmd prompts



# Globals
# blocked: used to ensure recieved socket messages display on the terminal before the main menu blocks the command-line interface 
# This variable is set to 'True' right before a client emit with an expected response executes. The response will set it back to False.
__blocked = False

# sim_mode: used to ensure functions do not attempt blocking user-input features 
__sim_mode = False

# tempNodeList: used to hold the order of which nodes are sending requests...
#	...so that when the response comes in, data can be assigned properly
tempNodeList = []

# created_nodes: used to hold all created CRTS USRP Nodes objects
created_nodes = []

# registered_nodes: nodes that have requested to be registered with the SAS
registered_nodes = []

# Parser extracts command line flags/parameters  
parser = ArgumentParser(description='SAS USRP RX Interface Script - Provide a server address and port in order to connect to the SAS.')

# Socket Params----------------------------------------------------------------------------
parser.add_argument('-a','--address',\
		help='Server address. Example: -a \'127.0.0.1\'',\
		default='127.0.0.1')
parser.add_argument('-p','--port',\
		help='Server port. Example: -p 65432',\
		default='5000')
#------------------------------------------------------------------------------------------

# Use Simulation File----------------------------------------------------------------------
parser.add_argument('-s','--sim',\
		help='Simulation File path (realative to socket_to_sas.py). Example: -s simulations/sim_one.json',\
		default=None)
#------------------------------------------------------------------------------------------

# Helper Functions--------------------------------------------------------------------------
def isVaildInt(value):
	"""
	Returns True if a value can be casted to an int
	"""
	try:
		int(value)
		return True
	except ValueError:
		print("'" + value + "' is not a vaild int")
	return False

def printUsrpsAvailable():
	"""
	Prints out a list of avaiable USRPs on the network. Exact same as 'uhd_find_devices' macro.
	"""
	usrps = list(uhd.find_devices())
	for usrp in usrps:
		print(usrp)

def _grabPossibleEntry(entry, key):
	"""
	Takes a dictionary entry and checks to see if it exists
	TODO
	"""
	try:
		if(entry[key]):
			print("entry not empty")
		else:
			print("entry empty")
	except KeyError:
		print("Entry does not have a '" + key + "'' as a key")

def send_params(clientio, node):
	"""
	Collects current node parameters and sends to host via socket as JSON

	Parameters
	----------
	clientio : socket object
		socket connection to host
	node : SDR object
		USRP object to gather operating parameters from
	"""

	data = {
		"SDR Address": node.get_SDR_Address(),
		"Center Frequency": node.get_freq(),
		"Gain": node.get_gain(),
		"Sample Rate": node.get_signal_amp(),
		"Signal Amplitude": node.get_signal_amp(),
		"Waveform": str(node.get_waveform()),
		"Status": node.get_status()
	}
	payload = json.dumps(data)
	clientio.emit('getNodeParams', payload)

def updateRadio(node, params):
	"""
	Updates radio operating parameters

	Parameters
	----------
	node : SDR object
		USRP object to gather operating parameters from
	params : dictionary
		JSON package of parameters to update
	"""

	# check params for every key:value pair
	params = json.loads(params)
	if "freq" in params:
		node.set_freq(float(params['freq'])*1e6)
	if "gain" in params:
		node.set_gain(int(params['gain']))
	if "samplerate" in params:
		node.set_sample_rate(int(params['samplerate'])*1e6)
	if "sigamp" in params:
		signalAmp = float(params['sigamp'])
		if signalAmp > 1:
			signalAmp = 1
		node.set_signal_amp(signalAmp)
	if "waveform" in params:
		waveform  = (params['waveform'])
		node.set_waveform(waveform)
	if "device" in params:
		node.set_SDR_Address(params['device'])
	if "status" in params:
		node.set_status(params['status'])

	# Ack to server with new params
	# send_params(clientio, node)

def findNodeFromTempListByIndex(index):
	"""
	Helper Function to find Nodes in created_nodes with a given identifier 

	Parameters
	----------
	index : int
		index of tempList

	Returns
	-------
	node : Node Object
		The Node object with the given identifier 
	"""
	iter = 0
	for node in created_nodes:
		if(node.get_SDR_Address() == tempNodeList[iter]):
			return node
		else:
			iter = iter + 1
	return None
# End Helper Functions--------------------------------------------------------------------------



def simCreateNode(items):
	"""
	Creates nodes based on simulation file and adds them to created_nodes array

	Parameters
	----------
	items : array of dictionaries with Node data

	TODO: Make sure the data can create a vaild USRP
	TODO: Is this just for TX? What params would RX need instead?
	TODO: Decide what KeyErrors should hault node creation
	"""
	global created_nodes
	for data in items:
		usrpMode = address = centerFreq = gain = sampleRate = signalAmp = waveform = None
		try:
			if(data["mode"] != ""):
				usrpMode = data["mode"]
		except KeyError:
			print("No mode found for simCreateNode (socket_to_usrp.py line 101)")
		try:
			if(data["address"] != ""):
				address = data["address"]
		except KeyError:
			print("No address found for simCreateNode (socket_to_usrp.py line 113)")
		try:
			if(data["centerFreq"] != ""):
				centerFreq = data["centerFreq"]
		except KeyError:
			print("No centerFreq found for simCreateNode (socket_to_usrp.py line 118)")
		try:
			if(data["gain"] != ""):
				gain = data["gain"]
		except KeyError:
			print("No gain found for simCreateNode (socket_to_usrp.py line 123)")
		try:
			if(data["sampleRate"] != ""):
				sampleRate = data["sampleRate"]
		except KeyError:
			print("No sampleRate found for simCreateNode (socket_to_usrp.py line 128)")
		try:
			if(data["signalAmp"] != ""):
				signalAmp = data["signalAmp"]
		except KeyError:
			print("No signalAmp found for simCreateNode (socket_to_usrp.py line 133)")
		try:
			if(data["waveform"] != ""):
				waveform = data["waveform"]
		except KeyError:
			print("No waveform found for simCreateNode (socket_to_usrp.py line 138)")

		node = tx_usrp(address, centerFreq, gain, sampleRate, signalAmp, waveform, None, usrpMode) # Create instance of USRP Node with given params
		if(node):
			created_nodes.append(node)
		else:
			print("Node NOT created (socket_to_sas.py line 161)")


def cmdCreateNode():
	"""
	Walks a user through the command line to configure a USRP node

	Depedancies: cmd_prompts.py, tx_usrp.py

	"""
	global created_nodes
	node = None
	usrpMode = promptUsrpMode()
	sdrAddr = promptUsrpIpAddr()
	# TODO: Now that IP is entered, maybe just pull more info from UHD and save it?
	cFreq = promptUsrpCenterFreq()
	if(usrpMode == 'TX'):
		# TODO: find min/max for all of these
		usrpGain = promptUsrpGain()
		sampleRate = promptUsrpSampleRate()
		signalAmp = promptUsrpSignalAmp()
		waveform = promptUsrpWaveform()
		node = tx_usrp(sdrAddr, cFreq, usrpGain, sampleRate, signalAmp, waveform, "", usrpMode) # Create instance of Tx with given params
	elif(usrpMode == 'RX'):
		pass # Big TODO
	else:
		print("Error")
	if(node):
		created_nodes.append(node)
	else:
		print("Node NOT created (socket_to_sas.py line 161)")


def simRegistrationReq(items):
	"""
	Simulation file provides data to create a Registration Request

	Since there may be multiple registartion requests at once, there is a for loop. 
	The value of 'request' should be a single registration request. 

	Parameters
	----------
	items : array of Registration Request data (dict format)
	"""
	arr = []
	global tempNodeList
	tempNodeList = []
	for request in items:
		nodeIp = userId = fccId = callSign = cbsdCategory = cbsdInfo = airInterface = None
		installationParam = measCapability = groupingParam = cpiSignatureData = None
		try:
			if(request["nodeIp"] != ""):
				nodeIp = request["nodeIp"]
		except KeyError:
			print("No nodeIp found for simRegistrationReq (socket_to_usrp.py line 144)")
		try:
			if(request["userId"] != ""):
				userId = request["userId"]
		except KeyError:
			print("No userId found for simRegistrationReq (socket_to_usrp.py line 149)")
		try:
			if(request["fccId"] != ""):
				fccId = request["fccId"]
		except KeyError:
			print("No fccId found for simRegistrationReq (socket_to_usrp.py line 154)")
		try:
			if(request["callSign"] != ""):
				callSign = request["callSign"]
		except KeyError:
			print("No callSign found for simRegistrationReq (socket_to_usrp.py line 159)")
		try:
			if(request["cbsdCategory"] != ""):
				cbsdCategory = request["cbsdCategory"]
		except KeyError:
			print("No cbsdCategory found for simRegistrationReq (socket_to_usrp.py line 164)")
		try:
			if(request["cbsdInfo"] != ""):
				cbsdInfo = request["cbsdInfo"]
		except KeyError:
			print("No cbsdInfo found for simRegistrationReq (socket_to_usrp.py line 169)")
		try:
			if(request["airInterface"] != ""):
				airInterface = request["airInterface"]
		except KeyError:
			print("No airInterface found for simRegistrationReq (socket_to_usrp.py line 174)")
		try:
			if(request["installationParam"] != ""):
				installationParam = request["installationParam"]
		except KeyError:
			print("No installationParam found for simRegistrationReq (socket_to_usrp.py line 179)")
		try:
			if(request["measCapability"] != ""):
				measCapability = request["measCapability"]
		except KeyError:
			print("No measCapability found for simRegistrationReq (socket_to_usrp.py line 184)")
		try:
			if(request["groupingParam"] != ""):
				groupingParam = request["groupingParam"]
		except KeyError:
			print("No groupingParam found for simRegistrationReq (socket_to_usrp.py line 189)")
		try:
			if(request["cpiSignatureData"] != ""):
				cpiSignatureData = request["cpiSignatureData"]
		except KeyError:
			print("No cpiSignatureData found for simRegistrationReq (socket_to_usrp.py line 194)")
		
		# If all data is good, at Node IP to the list for the reponse handler to pull out
		tempNodeList.append(nodeIp)



def configRegistrationReq():
	"""
	Pulls Registration Request Info from a file the user selects
	"""
	pass

def cmdRegistrationReq():
	"""
	Provides Command Line Prompts for a user to create Registration Request(s)
 
	Note: UHD Lib provides the serial, addr, and model ('type' for the uhd lib) for all usrps. Nodes with an FPGA includes the fpga.
		  Some 'type' matches with their 'product'. If there is a 'product', it is the same as the 'type' (e.g. x300).
		  When 'product' doesn't exist, it seems to be of type 'usrp2' 

		 TODO Change from "How many ..." to "Do you wanna do another?") && Is type USRP model?
	"""
	arr = []
	global tempNodeList
	tempNodeList = []

	num = promptNumOfRequests("How many Registration Requests would you like to create at this moment?: ")
	for x in range(num):
		userId = input("Enter User ID: ")
		fccId = input("Enter FCC ID: ")
		cbsdSerialNumber = promptCbsdSerial(created_nodes)
		tempNodeList.append(cbsdSerialNumber)
		callSign = input("Enter Call Sign (Optional - Press Enter to Skip): ")
		cbsdCategory = promptCbsdCategory()
		cbsdInfo = promptCbsdInfo(cbsdSerialNumber, created_nodes)
		airInterface = promptAirInterface()
		installationParam = None
		installationInfoSelector = getSelectorBoolean(input("Do you want to enter Device Installation Information (Y)es or (N)o: "))
		if(installationInfoSelector):
			installationParam = promptInstallationParam()
		measCapability = getMeasCapabilityFromUser()
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

def registrationRequest(clientio, items):
	"""
	Function that should always be called for a Registration Request

	Parameters
	----------
	clientio : socket Object
		Socket connection to the SAS
	items : array of Requests data
		Only used if the sim file is calling this funciton
	"""

	if(__sim_mode):
		simRegistrationReq(items)
	else:
		while(True):
			data_source = input("Would you like to manually enter the registraion info or load from a file? (E)nter or (L)oad: ")
			if(data_source == 'E' or data_source == 'e'):
				arrOfRequest = cmdRegistrationReq() # Prompt User
				break
			elif(data_source == 'L' or data_source == 'l'):
				arrOfRequest = configRegistrationReq() # load config file
				break
			elif(data_source == 'exit'):
				return
			else:
				print("Invalid Entry... Please enter 'E' for Manual Entry or 'L' to load from a config file...")
	# Need to save list of nodes being registered...
	
	payload = {"registrationRequest": arrOfRequest}
	clientio.emit("registrationRequest", json.dumps(payload))

def handleRegistrationResponse(clientio, payload):
	"""
	Receives data from SAS after a Registration Request is made

	TODO: If SAS doesnt give all required info, then ignore the fact that we sent a request

	Parameters
	----------
	payload : JSON string
		Registration response data
	clientio : socketio Object
		Socket connection
	"""
	json_data = json.loads(payload)
	responseCode = "error"
	cbsdId = "error" 
	responseMessage = ""
	global tempNodeList  # Array of IP Addresses
	global created_nodes # Array of nodes (usrp objects)
	iter = 0
	for regResponse in json_data["registrationResponse"]:
		print(regResponse)
		if(regResponse["cbsdId"]):
			cbsdId = regResponse["cbsdId"]
			for node in created_nodes: # Find the node object this request went with
				if(node.get_SDR_Address() == tempNodeList[iter]):
					node.set_CbsdId(cbsdId)
					print(node.get_SDR_Address() + " goes with " + node.get_CbsdId())
		if(regResponse["measReportConfig"]):
			measReportConfig = regResponse["measReportConfig"]
		if(regResponse["response"]):
			response = regResponse["response"]
			if(response["responseCode"]):
				responseCode = response["responseCode"]
				if(isVaildInt(responseCode)):
					print("Response Code: " + responseDecode(int(responseCode)))
			if(response["responseMessage"]):
				responseMessage = response["responseMessage"]
			if(response["responseData"]):
				responseData = response["responseData"]
			if(responseCode == "0"):
				print("Registration Successful!")
				if(cbsdId):
					print("Assigned CBSD ID: " + cbsdId)
					node.set_Cbsd(cbsdId)
				print("Response Message: " + responseMessage)



def configSpectrumInquiryReq():
	"""
	"""
	pass

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

def spectrumInquiryRequest(clientio):
	"""
	Sends Spectrum Inquiry Request to the SAS
	"""
	arrOfRequest = None
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
	Handles Spectrum Inquiry response from the SAS
	"""
	jsonData = json.loads(data)
	for SIResponse in jsonData["spectrumInquiryResponse"]:
		print(SIResponse)
		if(SIResponse["cbsdId"]):
			cbsdId = SIResponse["cbsdId"]
		if(SIResponse["availableChannel"]):
			availableChannel = SIResponse["availableChannel"]
		if(SIResponse["response"]):
			response = SIResponse["response"]
			if(response["responseCode"]):
				responseCode = response["responseCode"]
				if(isVaildInt(responseCode)):
					print("Response Code " + int(responseCode)+ ": " + responseDecode(int(responseCode)))
			if(response["responseMessage"]):
				responseMessage = response["responseMessage"]
			if(response["responseData"]):
				responseData = response["responseData"]


def configGrantReq():
	"""
	"""
	pass

def cmdGrantReq(clientio):
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

def grantRequest(clientio, txUsrp):
	"""
	Creates a Grant Request and sends it to the SAS
	"""
	arrOfRequest = None
	while(True):
		dataSource = input("Would you like to manually enter the Grant Request info or load from a file? (E)nter or (L)oad: ")
		if(dataSource == 'E' or dataSource == 'e'):
			arrOfRequest = cmdGranReq()
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
	Handles Grant Response message from SAS to CBSD
	TODO: Ensure if this is sucessful, CBSD holds value of the active grant it is assigned to
	"""
	jsonData = json.loads(data)
	for grantResponse in jsonData["grantResponse"]:
		print(grantResponse)
		if(grantResponse["cbsdId"]):
			cbsdId = grantResponse["cbsdId"]
		if(grantResponse["grantId"]):
			grantId = grantResponse["grantId"]
		if(grantResponse["grantExpireTime"]):
			grantExpireTime = grantResponse["grantExpireTime"]
		if(grantResponse["heartbeatInterval"]):
			heartbeatInterval = grantResponse["heartbeatInterval"]
		if(grantResponse["measReportConfig"]):
			measReportConfig = grantResponse["grantResponse"]
		if(grantResponse["operationParam"]):
			operationParam = grantResponse["operationParam"]
		if(grantResponse["channelType"]):
			channelType = grantResponse["channelType"]
		if(grantResponse["response"]):
			response = grantResponse["response"]


def configHeartbeatReq():
	"""
	Loads a heartbeat request form from a JSON file
	"""
	pass

def cmdHeartbeatReq():
	"""
	Prompts user through creating a Heartbeat request
	"""
	arr = []
	cbsd = None
	# Print registered nodes' CBSD ID's
	print("Registered CBSD IDs:")
	for node in registered_nodes:
		print("\t"+node.get_CbsdId())
	cbsdId = input("Enter CBSD of node you want to use for the heartbeat request: ")
	for node in registered_nodes:
		if(node.get_CbsdId() == cbsdId):
			cbsd = node
	grantId = cbsd.get_GrantId() # TODO: error handle this
	grantRenew = getSelectorBoolean(input("Would you like to renew the grant? (Y)es or (N)o: "))
	operationState = input("Is this CBSD AUTHORIZED or GRANTED: ") # @Joseph Either 'AUTHORIZED' or 'GRANTED'. Which is which, I forget
	measReport = None
	provideRcvdPowerMeas = getSelectorBoolean(input("Do you want to provide Received Power Measurments to the SAS? (Y)es or (N)o: "))
	if(provideRcvdPowerMeas):
		rcvdReport = promptRcvdPowerMeasReport()
		measReport = MeasReport([rcvdReport])
	arr.append(HeartbeatRequest(cbsdId, grantId, grantRenew, operationState, measReport).asdict())
	return arr

def heartbeatRequest(clientio):
	"""
	Creates a heartbeat request to send to the SAS
	"""
	while(True):
		dataSource = input("Would you like to manually enter the Heartbeat Request info or load from a file? (E)nter or (L)oad: ")
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
	payload = {"heartbeatRequest": arrOfRequest}
	clientio.emit("heartbeatRequest", json.dumps(payload))

def handleHeartbeatResponse(clientio, data):
	"""
	Handles Heartbeat Response message from SAS to CBSD
	"""
	jsonData = json.loads(data)
	for hbResponse in jsonData["heartbeatResponse"]:
		print(hbResponse)
		if(hbResponse["cbsdId"]):
			cbsdId = hbResponse["cbsdId"]
		if(hbResponse["grantId"]):
			grantId = hbResponse["grantId"]
		if(hbResponse["transmitExpireTime"]):
			transmitExpireTime = hbResponse["transmitExpireTime"]
		if(hbResponse["grantExpireTime"]):
			grantExpireTime = hbResponse["grantExpireTime"]
		if(hbResponse["heartbeatInterval"]):
			heartbeatInterval = hbResponse["heartbeatInterval"]
		if(hbResponse["operationParam"]):
			operationParam = hbResponse["operationParam"]
		if(hbResponse["measReportConfig"]):
			measReportConfig = hbResponse["measReportConfig"]
		if(hbResponse["response"]):
			response = hbResponse["response"]


def configRelinquishmentReq():
	"""
	"""
	pass

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

def relinquishmentRequest(clientio):
	"""
	Creates Relinishment Request to send to the SAS
	"""
	while(True):
		dataSource = input("Would you like to manually enter the Relinquishment Request info or load from a file? (E)nter or (L)oad: ")
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
	Handles data returned from SAS regarding previously sent Relinquishment Request
	"""
	jsonData = json.loads(data)
	for relinquishment in jsonData["relinquishmentResponse"]:
		print(relinquishment)
		if(relinquishment["cbsdId"]):
			cbsdId = relinquishment["cbsdId"]
		if(relinquishment["grantId"]):
			grantId = relinquishment["grantId"]
		if(relinquishment["response"]):
			response = relinquishment["response"]


def configDeregistrationReq():
	"""
	"""
	pass

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

def deregistrationReq(clientio):
	"""
	Creates a Deregistration request and sends it to the SAS
	"""
	while(True):
		dataSource = input("Would you like to manually enter the Deregistration Request info or load from a file? (E)nter or (L)oad: ")
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
	"""
	jsonData = json.loads(data)
	for dereg in jsonData["deregistrationResponse"]:
		if(dereg["cbsdId"]):
			cbsdId = dereg["cbsdId"]
		if(dereg["response"]):
			response = dereg["response"]



def stopNode(cbsdId):
	"""
	Takes CBSD ID and finds associated node and turns it off
	"""
	for node in created_nodes:
		if(node.get_CbsdId() == cbsdId):
			node.stop()
			return
	print("No node found with CBSD ID: " + cbsdId)

def startNode(cbsdId):
	"""
	Turns on the Node with the provided CBSD ID
	"""
	for node in created_nodes:
		if(node.get_CbsdId == cbsdId):
			node.start()
			return
	print("No node found with CBSD ID: " + cbsdId)


def defineSocketEvents(clientio):
	"""
	List of events the SAS may echo, and how to handle them
	"""
	@clientio.event
	def connect():
		print('connection established. Given sid: ' + clientio.sid)

	@clientio.event
	def identifySource():
		clientio.emit("identifySource", ("I am CRTS"))
		# send_params(clientio, txUsrp)
		# registrationReq(clientio)

	# Official WinnForum Predefined Functionality
	@clientio.event
	def registrationResponse(data):
		global __blocked
		handleRegistrationResponse(clientio, data)
		__blocked = False

	@clientio.event
	def sprectumInquiryResponse(data):
		global __blocked
		handleSpectrumInquiryResponse(clientio, data)
		__blocked = False

	@clientio.event
	def grantResponse(data):
		global __blocked
		handleGrantResponse(clientio, data)
		__blocked = False

	@clientio.event
	def heartbeatResponse(data):
		global __blocked
		handleHeartbeatResponse(clientio, data)
		__blocked = False

	@clientio.event
	def relinquishmentResponse(data):
		global __blocked
		handleRelinquishmentResponse(clientio, data)
		__blocked = False

	@clientio.event
	def deregistrationResponse(data):
		global __blocked
		handleDeregistrationResponse(clientio, data)
		__blocked = False
	# end official WinnForum functions

	@clientio.event
	def getTxParams(node):
		send_params(clientio, node)

	@clientio.event
	def updateParams(cbsdId, newParams):
		updateRadio(cbsdId, newParams)

	@clientio.event
	def stop_radio(cbsdId):
		stopNode(cbsdId)

	@clientio.event
	def start_radio(cbsdId):
		startNode(cbsdId)

	# TODO - cbsdID and measReport
	# @clientio.event
	# def sendSpectrumData():
	# 	pass
	# @clientio.event
	# def operationParams(data):
	# 	pass

	@clientio.event
	def disconnect():
		print('Server terminated connection')

def init(clientio, args):
	"""
	Create radio object and connects to server

	Parameters
	----------
	args : list
		List of parameters extracted from command line flags
	"""

	# Create handlers for events the SAS may emit
	defineSocketEvents(clientio)

	# Connect to SAS
	socket_addr = 'http://' + args['address'] +':' + args['port']
	clientio.connect(socket_addr)

	# Create global array of USRPs for use across functions
	# TODO: I should not have to reiterate what created_node is in here since I READ_ONLY in here
	# global created_nodes
	# created_nodes = []

	if(args['sim']):
		'''
		Simulation file includes all requests to make and at what times
		This requires no human interaction with the program. There may be output to read in the terminal.
		'''
		global __sim_mode
		__sim_mode = True
		#load sim file
		# Check all actions to complete at a given time. If there are duplicates, 
		# make sure they get sent in the same array/payload
		path = args['sim']
		with open(path) as config:
			data = json.load(config)
		for time in data:
			for action in data[time]:
				for func in action:
					print("Going to execute: " + func)
					payload = action[func]
					if(func == "createNode"):
						pass
					elif(func == "registrationRequest"):
						pass
					elif(func == "spectrumInquiryRequest"):
						pass
					elif(func == "grantRequest"):
						pass
					elif(func == "heartbeatRequest"):
						pass
					elif(func == "relinquishmentRequest"):
						pass
					elif(func == "deregistrationRequest"):
						pass
					#send payload to appropiate function
		
	else:
		# Main Menu
		# CMD is blocking sockets from printing until user enters another value
		# To remedy this, I may add a boolean that is True when the socket is busy 
		# Once the socket is done completeing the action the user entered, the bool
		# should allow the loop to proceed... TODO
		cmdCreateNode()
		global __blocked
		__blocked = False
		print("Enter 'h' for help/list of commands")
		while True:
			while not __blocked:
				user_input = input("User Input: ")
				if(user_input == 'h'):
					print("""Commands Include:
						0 - Exit Interface
						1 - Create USRP
						2 - View Nodes
						3 - Create Registration Request
						4 - Create Spectrum Inquiry Request
						5 - Create Grant Request
						6 - Create Heartbeat Request
						7 - Create Relinquishment Request
						8 - Create Deregistration Request
						""")
				elif(userInput == '0'):
					print("Exiting System...")
					sys.exit()
				elif(userInput == '1'):
					created_nodes.append(cmdCreateNode())
				elif(userInput == '2'):
					viewNodes()
				elif(userInput == '3'):
					__blocked = True
					registrationRequest(clientio, None)
				elif(userInput == '4'):
					__blocked = True
					spectrumInquiryRequest(clientio)
				elif(userInput == '5'):
					__blocked = True
					grantRequest()
				elif(userInput == '6'):
					__blocked = True
					heartbeatRequest()
				elif(userInput == '7'):
					__blocked = True
					relinquishmentRequest()
				elif(userInput == '8'):
					__blocked = True
					deregistrationRequest()
		
	print("Exiting System...")
	sys.exit()


if __name__ == '__main__':
	args = vars(parser.parse_args())	# Get command line arguments
	clientio = socketio.Client()		# Create Client Socket
	init(clientio, args)				# Init Tx USRP and Socket
	clientio.wait()					 	# Wait for Socket Events TODO: Doesn't reach here?
	