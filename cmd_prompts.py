#!/usr/bin/env python3

# Author: Cam Makin
# For Research Efforts: Wireless@VT
# Description: User Library for Command Line Prompts. Used for by socket_to_sas.py 
# Last Updated: 01/05/2021

from WinnForum import CbsdInfo, InstallationParam, FrequencyRange, OperationParam, VTGrantParams
from gnuradio import uhd

# Helpers
def getSelectorBoolean(selection):
	"""
	Translates Yes and No to True and False
	"""
	data = selection
	while True:
		if(data == 'Y' or data == 'y'):
			return True
		elif(data == 'N' or data == 'n'):
			return False
		else:
			data = input("Please enter Y for Yes or N for No: ")

def getValidFloat(prompt):
	"""
	Prompts user with prompt and returns a float (or 'enter')
	"""
	while(True):
		value = input(prompt)
		if(value != ""): # If data is not 'enter'
			try:
				value = float(value)
				return value
			except ValueError:
				print("Please enter a valid number...")
		else:
			return value

def getValidInt(prompt):
	"""
	Prompts user to either enter an integer or 'enter' and returns the value

	TODO: Should I really allow this to pass ' "" ' if user presses enter?
	"""
	while(True):
		value = input(prompt)
		if(value != ""):
			try:
				value = int(value)
				return int(value)
			except ValueError:
				print("Please enter a vaild integer...")
		else:
			return value

def promptNumOfRequests(prompt):
	"""
	Prompts user to enter a non-negative integer for the # of requests they'd like to make
	"""
	while(True):
		num = getValidInt(prompt)
		if(num < 0):
			print("Please enter a value >= 0...")
		else:
			return num

# Create Node
def promptUsrpMode():
	"""
	Prompts User for USRP Mode (Either TX or RX)
	"""
	while True:
		usrpMode = input("What kind of USRP would you like to create? (T)x or (R)x?: ")
		if(usrpMode == 'T' or usrpMode == 't'):
			return 'TX'
		elif(usrpMode == 'R' or usrpMode == 'r'):
			return 'RX'
		else:
			print("Please enter T for a Transmitter or R for a Receiver...")

def promptUsrpIpAddr():
	"""
	Prompts User for valid USRP IP Address and cross references with UHD list

	**Maybe refresh usrps list after each attempt? In case a node becomes available.
	"""
	while(True):
		ip = input("Enter the IP Address of the node (Ex. 192.168.40.110): ")
		for node in list(uhd.find_devices()):
			if(ip == node['addr']):
				print("UHD Lib has found a node matching the IP you entered! Would you like to use info from UHD ")
				return ip
		keepIP = getSelectorBoolean(input("IP: " + ip + "not found by the UHD lib. Would you like still register this IP? Y/N: "))
		if(keepIP):
			return ip

def promptUsrpGain():
		"""
		Prompt user to enter Usrp Gain
		"""
		while(True):
			gain = getValidFloat("Enter USRP gain (in dB): ")
			# TODO: Check to ensure gain is in valid range
			return gain

def promptUsrpSampleRate():
	"""
	Prompts user to enter a valid sample rate

	TODO: ensure sampRate is in range
	"""
	while(True):
		sampRate = getValidFloat("Enter Sample Rate of the node (in Hz): ")
		return sampRate

def promptUsrpCenterFreq():
	"""
	Prompt user to enter center frequency of Tx/Rx 
	"""
	while(True):
		cfreq = input("Enter the center frequency of the node (in Hz): ")
		if(int(cfreq) < 0):
			print("Please enter a positive integer for frequency...")
		else:
			return int(cfreq)

def promptUsrpSignalAmp():
	"""
	Prompts user to enter a vaild signal amplitude [0,1]
	"""
	while(True):
		sigamp = input("Enter the Signal Amplitude (0 to 1): ")
		if(float(sigamp) < 0 or float(sigamp) > 1):
			print("Amplitude must be a vaule between 0 and 1...")
		else:
			return sigamp

def promptUsrpWaveform():
	"""
	Prompts user to enter a valid waveform
	"""
	while(True):
		waveforms = ["CONSTANT", "SINE", "COSINE", "SQUARE", "TRIANGLE", "SAWTOOTH"]
		wf = input('Enter waveform type (Valid Inputs: CONSTANT, SINE, COSINE, SQUARE, TRIANGLE, SAWTOOTH): ')
		if(wf.upper() not in waveforms):
			print(wf + " is not a vaild waveform option...")
		else:
			return wf.upper()


# Registration Request
def promptCbsdSerial(usrps):
	"""
	Prompts user for a vaild CBSD Serial Number and cross references with uhd_find_devices

	Returns: cbsdSerialNumber (string)
	"""
	for node in usrps:
		print(node.get_SDR_Address())
	while(True): # TODO This will get stuck if there isnt a vaild Serial...
		cbsdSerialNumber = input("Enter CBSD Serial Number: ")
		for node in usrps:
			if(cbsdSerialNumber == node['serial']):
				return cbsdSerialNumber
		print("No vaild USRP found with serial: " + cbsdSerialNumber)

def promptCbsdCategory():
	"""
	Prompts user for valid CBSD Category information
	"""
	while True:
		cbsdCategory = input("Enter CBSD Category ('A' or 'B'): ")
		if(cbsdCategory == 'a' or cbsdCategory == 'A'):
			return 'A'
		elif(cbsdCategory == 'b' or cbsdCategory == 'B'):
			return 'B'
		elif(cbsdCategory == ""):
			return None
		else:
			print("Invlaid CBSD Category...")

def promptCbsdInfo(cbsdSerialNumber, usrps):
	"""
	Prompts User for info to build CBSD Info object. Can only pull model info with the given info from UHD.

	Parameters:
		cbsdSerialNumber: The serial of the desired USRP to pull info from.
	"""
	cbsdInfoSelector = getSelectorBoolean(input("Do you want to enter CBSD Device Information (Y)es or (N)o: "))
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
	"""
	latitude = getValidFloat("Enter latitude: ")
	longitude = getValidFloat("Enter longitude: ")
	height = getValidFloat("Enter antenna height (in meters): ")
	while(True):
		heightType = input("Enter height type ('AGL' for relative to ground level or 'AMSL' for realtive to mean sea level: ")
		if(heightType != 'AGL' and heightType != 'AMSL' and heightType != ""):
			print("Please enter 'AGL' or 'AMSL'...")
		else:
			break
	horizontalAccuracy = getValidFloat("Enter horizontal accuracy (in meters): ")
	verticalAccuracy = getValidFloat("Enter vertical accuracy: ")
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
			if(antennaAzimuth < 0 or antennaAzimuth > 359):
				print("Please enter a value between 0 and 359 (inclusive)...")
			else:
				break
		except ValueError:
			print("Please enter a vaild number...")
	while(True):
		antennaDowntilt = input("Enter Antenna Downtilt (-90 to 90 degrees, Negative is tilted UP): ")
		if(antennaDowntilt == ""):
			break
		try:
			antennaDowntilt = float(antennaDowntilt)
			if(antennaDowntilt < -90 and antennaDowntilt > 90):
				print("Please enter an angle between -90 and 90 (inclusive)...")
			else:
				break
		except ValueError:
			print("Please enter a vaild number...")
	antennaGain = input("Peak Antenna Gain (-127 to 128 dBi): ")
	eirpCapability = input("Enter Max EIRP (between -127 and +47) (in dBm/10MHz): ")
	antennaBeamwidth = input("Enter Antenna Beamwidth (3-dB antenna beamwidth of the antenna in the horizontal-plane in degrees): ")
	antennaModel = input("If there is an external antenna, enter the model information: ")
	installationParam = InstallationParam(latitude, longitude, height, heightType, horizontalAccuracy, verticalAccuracy, 
	indoorDeployment, antennaAzimuth, antennaDowntilt, antennaGain,	eirpCapability, antennaBeamwidth, antennaModel)
	return installationParam


# Spectrum Inquiry Request
def promptFrequencyRange():
	"""
	Prompts user to enter min and max frequency in Hz
	"""
	while(True):
		minFreq = getValidInt("Enter low frequency (in Hz): ")
		maxFreq = getValidInt("Enter high frequency (in Hz): ")
		if(minFreq > maxFreq):
			print("Minimum/Low Frequency (" + minFreq + ") cannot be greater than Maximum/High Frequency (" + maxFreq + ")...")
		else:
			return FrequencyRange(minFreq, maxFreq)


def promptRcvdPowerMeasReport():
	"""
	Prompts user to enter 
	"""
	measFreq = getValidInt("Enter Low Frequency of the  spectrum (in Hz): ")
	measBand = getValidInt("Enter measurement bandwidth where Low Frequency + bandwidth = High Frequency (in Hz): ")
	measRcvdPower = getValidFloat("Enter the dBm value that USRP sees at the  receiver (between -100 and -25 dBm): ")
	rcvdPowerMeasReport = RcvdPowerMeasReport(measFreq, measBand, measRcvdPower)
	return rcvdPowerMeasReport

# Grant Request
def promptOperationParam():
	"""
	Prompts user to enter information related to building a OperationParam object
	"""
	maxEirp = input("Enter Max EIRP (dBm/MHz) (-137 to +37): ")
	freqRange = promptFrequencyRange()
	return OperationParam(maxEir, freqRange)
	 
def promptVtGrantParams():
	"""
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
	mobility = getSelectorBoolean(input("Will this grant need to be mobile? (Y)es or (N)o: "))
	maxVelocity = None
	if(mobility):
		maxVelocity = input("Enter approximate byte size of data: ")
	return VTGrantParams(minFrequency, maxFrequency, preferredFrequency, frequencyAbsolute, minBandwidth,
		maxBandwidth, preferredBandwidth, startTime, endTime, approximateByteSize, dataType, powerLevel, location, 
		mobility, maxVelocity)