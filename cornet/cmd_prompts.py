#!/usr/bin/env python3

# Author: Cam Makin
# For Research Efforts: Wireless@VT
# Description: User Library for Command Line Prompts. Used for by socket_to_sas.py 
# Last Updated: 01/05/2021

from WinnForum import CbsdInfo, InstallationParam, FrequencyRange, OperationParam, VTGrantParams, RcvdPowerMeasReport
from gnuradio import uhd

# Helper Functions -----------------------------------------------------------------
def getSelectorBoolean(prompt):
	"""
	Prompts user a Y/N question and translates value to True and False.
	If user enters "exit", then function returns 'None'

	Parameters
	----------
	prompt : string
		Prompt that asks a Y/N question
	
	Returns
	-------
	user_input : boolean
		If user enters Yes, returns True; if No, False; if "exit", None
	"""
	while True:
		user_input = input(prompt)
		if(user_input == 'Y' or user_input == 'y'):
			return True
		elif(user_input == 'N' or user_input == 'n'):
			return False
		elif(user_input == "exit"):
			return None
		else:
			print("Please enter Y for Yes or N for No...")

def _getValidFloat(prompt):
	"""
	Prompts user with prompt and returns a float (or 'exit')
	If user enters 'exit' then this function returns 'None'
	"""
	while(True):
		user_input = input(prompt)
		if(user_input == "exit"):
			return None
		try:
			return float(user_input)
		except ValueError:
			print("Please enter a valid number (or 'exit' to quit this operation)...")

def _getValidInt(prompt):
	"""
	Prompts user to either enter an integer or 'enter' and returns the value

	TODO: Should I really allow this to pass ' "" ' if user presses enter?
	"""
	while(True):
		user_input = input(prompt)
		if(user_input == "exit"):
			return None
		try:
			return int(user_input)
		except ValueError:
			print("Please enter a vaild integer or 'exit' to quit...")

def promptNumOfRequests(prompt):
	"""
	Prompts user to enter a non-negative integer for the # of requests they'd like to make
	"""
	while(True):
		num = _getValidInt(prompt)
		if(num < 0):
			print("Please enter a value >= 0...")
		else:
			return num
# End Helper Functions -------------------------------------------------------------

# Disconnect from SAS
def promptSASDisconnect():
	return getSelectorBoolean("This action will void all grants and turn off all USRPs. Are you sure you want to disconnect from the SAS?")

# Create Node
def promptUsrpMode():
	"""
	Prompts User for USRP Mode (Either TX or RX)
	"""
	while(user_input := input("What kind of USRP would you like to create? (T)x or (R)x?: ")):
		if(user_input == 'T' or user_input == 't'):
			return "TX"
		elif(user_input == 'R' or user_input == 'r'):
			return "RX"
		elif(user_input == "exit"):
			return None
		else:
			print("Please enter T for a Transmitter or R for a Receiver or 'exit'...")

def promptUsrpIpAddr():
	"""
	Prompts User for valid USRP IP Address and cross references with UHD list

	TODO: Maybe refresh usrps list after each attempt? In case a node becomes available.
	"""
	while(ip := input("Enter the IP Address of the node (Ex. 192.168.40.110): ")):
		for node in list(uhd.find_devices()):
			if(ip == node['addr']):
				print("UHD Lib has found a node matching the IP you entered!")
				return ip
		keepIP = getSelectorBoolean("IP: " + ip + "not found by the UHD lib. Would you like still register this IP? Y/N: ")
		if(keepIP):
			return ip

def promptUsrpGain(min_gain=0, max_gain=31.5):
		"""
		Prompt user to enter Usrp Gain
		"""
		while(gain := _getValidFloat("Enter USRP gain (in dB): ")):
			if(gain < min_gain):
				print("Gain of '" + gain + "' is below the minimum of '" + min_gain + "'.")
			elif(gain > max_gain):
				print("Gain of '" + gain + "' is above the maximum of '" + max_gain + "'.")
			return gain

def promptUsrpBandwidth(min_bw=0, max_bw=10000000):
	"""
	Prompts user to enter a valid integer for bandwidth.
	Bandwidth range may be set using the optional parameters.

	Parameters
	----------
	min_bw : int (optional)
		Minimum bandwidth. Default: 0Hz.
	max_bw : int (optional)
		Maximum bandwidth. Defualt 10000000 (10MHz).
	"""
	while(bandwidth := _getValidInt("Enter bandwidth (in Hz): ")):
		if(bandwidth < min_bw):
			print("Bandwidth must be greater than "+ str(min_bw) +".")
		elif(bandwidth > max_bw):
			print("Bandwidth must be less than "+ str(max_bw) +".")
		else:
			return bandwidth

def promptUsrpCenterFreq(max_fc=3700000000):
	"""
	Prompt user to enter Center Frequency
	"""
	while(cfreq := _getValidInt("Enter the Center Frequency (in Hz): ")):
		if(cfreq < 0):
			print("Please enter a positive integer for frequency...")
		elif(cfreq > max_fc):
			print("Invalid Value: Maximum allowed Center Frequency is "+str(max_fc)+"...")
		else:
			return cfreq

def promptUsrpSignalAmp():
	"""
	Prompts user to enter a vaild signal amplitude [0,1]
	"""
	while(sigamp := input("Enter the Signal Amplitude (0 to 1): ")):
		if(float(sigamp) < 0 or float(sigamp) > 1):
			print("Amplitude must be a vaule between 0 and 1...")
		else:
			return sigamp

def promptUsrpWaveform():
	"""
	Prompts user to enter a valid waveform
	"""
	waveforms = ["CONSTANT", "SINE", "COSINE", "SQUARE", "TRIANGLE", "SAWTOOTH"]
	while(wf := input('Enter waveform type (Valid Inputs: CONSTANT, SINE, COSINE, SQUARE, TRIANGLE, SAWTOOTH): ')):
		if(wf.upper() not in waveforms):
			print(wf + " is not a vaild waveform option...")
		else:
			return wf.upper()


# Registration Request
def promptCbsdIpAddress(created_nodes):
	"""
	Prompts user for a vaild CBSD IP Address and cross references with uhd_find_devices

	Parameters
	----------
	created_nodes : list of Node objects
		Node objects that have been created

	Returns
	-------
	cbsdSerialNumber : string
	"""
	print("Available Node IP Addresses:")
	iter = 0
	for node in created_nodes:
		print(str(iter := iter+1) +" - "+ node.get_SDR_Address())
	while(cbsdIp := input("Select Node to Register (1 - "+str(iter)+"): ")):
		if(cbsdIp == "exit"):
			return None
		else:
			try:
				selection = int(cbsdIp)
			except ValueError:
				print("UserInputError: Input must be an integer from 1 to "+str(iter)+".")
			else:
				for node in list(uhd.find_devices()):
					if(created_nodes[selection+1].getIpAddress() == node['addr']):
						return node['serial']
		print("No vaild USRP found with serial: " + str(cbsdSerialNumber))

def promptCbsdSerial(usrps):
	"""
	Prompts user for a vaild CBSD Serial Number and cross references with uhd_find_devices

	Parameters
	----------
	usrps : list of Node objects
		Node objects that have been created

	Returns
	-------
	cbsdSerialNumber : string
	"""
	for node in usrps:
		print(node.get_SDR_Address())
	while(cbsdSerialNumber := input("Enter CBSD Serial Number: ")): # TODO This will get stuck if there isnt a vaild Serial...
		if(cbsdSerialNumber == "exit"):
			return None
		else:
			for node in list(uhd.find_devices()):
				if(cbsdSerialNumber == node['serial']):
					return cbsdSerialNumber
		print("No vaild USRP found with serial: " + str(cbsdSerialNumber))

def promptCbsdCategory():
	"""
	Prompts user for valid CBSD Category information

	Returns
	-------
	cbsdCategory : char
		CBAS Category 'A' or 'B' (or None if user presses 'Enter')
	"""
	while(cbsdCategory := input("Enter CBSD Category ('A' or 'B'): ")):
		if(cbsdCategory == 'a' or cbsdCategory == 'A'):
			return 'A'
		elif(cbsdCategory == 'b' or cbsdCategory == 'B'):
			return 'B'
		elif(cbsdCategory == "exit"):
			return None
		else:
			print("Invlaid CBSD Category...")

def promptCbsdInfo(cbsdSerialNumber, usrps):
	"""
	Prompts User for info to build CBSD Info object. Can only pull model info with the given info from UHD.

	Parameters
	----------
	cbsdSerialNumber : string 
		The serial of the desired USRP to pull info from.
	usrps : array of

	Returns
	-------

	"""
	cbsdInfoSelector = getSelectorBoolean("Do you want to enter CBSD Device Information (Y)es or (N)o: ")
	cbsdInfo = None
	if(cbsdInfoSelector):
		print("All Device info is optional - press enter to skip any field...")
		vendor = input("Enter Device Vendor (Ex. NI): ")
		nodeFound = False
		# ** usrps is my own list of objects. Have to be wiser...
		# for node in usrps:
		# 	if(not nodeFound)
		# 		try:
		# 			if(cbsdSerialNumber == node['serial']):
		# 				if(node['type']):
		# 					model = node['type']
		# 					nodeFound = True
		# 				else:
		# 					break
		model = input("Enter Model Info: ")
		softwareVersion = input("Enter Software Version: ")
		hardwareVersion = input("Enter Hardware Version: ")
		firmwareVersion = input("Enter Firmware Version: ")
		cbsdInfo = CbsdInfo(vendor, model, softwareVersion, hardwareVersion, firmwareVersion)
	return cbsdInfo

def promptAirInterface():
	"""
	Prompt user for Air Interface

	Returns
	-------
	userInput : string
		User input that is a valid Air Interface
	"""
	ais = ["E_UTRA", "CAMBIUM_NETWORKS", "4G_BBW_SAA_1", "NR", "DOODLE_CBRS", "CW", "REDLINE", "TARANA_WIRELESS"]
	print("Valid Air Interfaces: " + str(ais))
	while True:
		userInput = input("Enter Air Interface (Optional - Press Enter to Skip): ")
		if(userInput == ""):
			return None
		elif(userInput not in ais):
			print("Please enter a vaild Air Interface or Press Enter to skip...")
		else:
			return userInput

def promptInstallationParam():
	"""
	Prompts user through Installation Parameter object definition

	Returns
	-------
	param : InstallationParam object
	"""
	latitude = _getValidFloat("Enter latitude: ")
	longitude = _getValidFloat("Enter longitude: ")
	height = _getValidFloat("Enter antenna height (in meters): ")
	while(True):
		heightType = input("Enter height type ('AGL' for relative to ground level or 'AMSL' for realtive to mean sea level: ")
		if(heightType != 'AGL' and heightType != 'AMSL' and heightType != ""):
			print("Please enter 'AGL' or 'AMSL'...")
		else:
			break
	horizontalAccuracy = _getValidFloat("Enter horizontal accuracy (in meters): ")
	verticalAccuracy = _getValidFloat("Enter vertical accuracy: ")
	while(True):
		indoorDeployment = input("Enter Deployment Type (0 for Outdoor or 1 for Indoor: ")
		if(indoorDeployment != '0' and indoorDeployment != '1'):
			print("Please enter '1' or '0'...")
		else:
			break
	while(True):
		antennaAzimuth = input("Enter the Horizontal Direction Angle for the Antenna (0 for True North, 90 for East, etc): ")
		if(antennaAzimuth == ""):
			break
		try:
			antennaAzimuth = float(antennaAzimuth)
		except ValueError:
			print("Please enter a vaild number...")
		else:
			if(antennaAzimuth < 0 or antennaAzimuth > 359):
				print("Please enter a value between 0 and 359 (inclusive)...")
			else:
				break
	while(True):
		antennaDowntilt = input("Enter Antenna Downtilt (-90 to 90 degrees, Negative is tilted UP): ")
		if(antennaDowntilt == ""):
			break
		try:
			antennaDowntilt = float(antennaDowntilt)
		except ValueError:
			print("Please enter a vaild number...")
		else:
			if(antennaDowntilt < -90 and antennaDowntilt > 90):
				print("Please enter an angle between -90 and 90 (inclusive)...")
			else:
				break
	antennaGain = input("Peak Antenna Gain (-127 to 128 dBi): ")
	eirpCapability = input("Enter Max EIRP (between -127 and +47) (in dBm/10MHz): ")
	antennaBeamwidth = input("Enter Antenna Beamwidth (3-dB antenna beamwidth of the antenna in the horizontal-plane in degrees): ")
	antennaModel = input("If there is an external antenna, enter the model information: ")
	installationParam = InstallationParam(latitude, longitude, height, heightType, horizontalAccuracy, verticalAccuracy, 
	indoorDeployment, antennaAzimuth, antennaDowntilt, antennaGain,	eirpCapability, antennaBeamwidth, antennaModel)
	return installationParam

def promptMeasCapability():
	"""
	Prompts user for Node measCapability

	TODO: Allow user to enter this/Pull these using USRP data.
	For now, they are hardcoded.
	
	Returns
	-------
	measCapability : array of string
	"""
	measCapabilities = [None]
	measCapabilities.append("RECEIVED_POWER_WITHOUT_GRANT")
	measCapabilities.append("RECEIVED_POWER_WITH_GRANT")
	return measCapabilities

# Spectrum Inquiry Request
def promptFrequencyRange():
	"""
	Prompts user to enter min and max frequency in Hz

	Returns
	-------
	range : FrequencyRange object
	"""
	while(True):
		minFreq = _getValidInt("Enter low frequency (in Hz): ")
		maxFreq = _getValidInt("Enter high frequency (in Hz): ")
		if(minFreq > maxFreq):
			print("Minimum/Low Frequency (" + minFreq + ") cannot be greater than Maximum/High Frequency (" + maxFreq + ")...")
		else:
			return FrequencyRange(minFreq, maxFreq)

def promptRcvdPowerMeasReport():
	"""
	Prompts user to enter MeasReport data

	Returns
	-------
	rcvdPowerMeasReport : RcvdPowerMeasReport object
	"""
	measFreq = _getValidInt("Enter Low Frequency of the  spectrum (in Hz): ")
	measBand = _getValidInt("Enter measurement bandwidth where Low Frequency + bandwidth = High Frequency (in Hz): ")
	measRcvdPower = _getValidFloat("Enter the dBm value that USRP sees at the  receiver (between -100 and -25 dBm): ")
	rcvdPowerMeasReport = RcvdPowerMeasReport(measFreq, measBand, measRcvdPower)
	return rcvdPowerMeasReport

# Grant Request
def promptOperationParam():
	"""
	Prompts user to enter information related to building a OperationParam object

	Returns
	-------
	param : OperationParam object
	"""
	maxEirp = input("Enter Max EIRP (dBm/MHz) (-137 to +37): ")
	freqRange = promptFrequencyRange()
	return OperationParam(maxEirp, freqRange)
	 
def promptVtGrantParams():
	"""
	Ask user to enter VT Grant Parameters.

	Returns
	-------
	params : VTGrantParams object
	"""
	minFrequency = input("Enter minimum acceptable operating frequency: ")
	maxFrequency = input("Enter maximum acceptable operating frequency: ")
	preferredFrequency = input("Enter desired center frequency: ")
	frequencyAbsolute = input("Enter absolue frequency: ") # TODO: what is this supposed to resemble?
	minBandwidth = input("Enter minimum acceptable bandwidth: ")
	maxBandwidth = input("Enter maximum acceptable bandwidth: ")
	preferredBandwidth = input("Enter prefered bandwidth: ")
	startTime = input("Enter desired grant start time: ")
	endTime = input("Enter desired grant end time: ")
	approximateByteSize = input("Enter approximate byte size of data: ")
	dataType = input("Enter data type being transferred (e.g. text, video, audio): ")
	powerLevel = input("Enter desired transmitter power output (in dBm): ")
	location = input("Enter location of grant transmission: ") # TODO: what location? Tx, desired Rx?
	mobility = getSelectorBoolean("Will this grant need to be mobile? (Y)es or (N)o: ")
	if(mobility):
		maxVelocity = input("Enter approximate byte size of data: ")
	else:
		maxVelocity = None
	return VTGrantParams(minFrequency, maxFrequency, preferredFrequency, frequencyAbsolute, minBandwidth,
		maxBandwidth, preferredBandwidth, startTime, endTime, approximateByteSize, dataType, powerLevel, location, 
		mobility, maxVelocity)