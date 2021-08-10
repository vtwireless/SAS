# SAS Core
This folder contains everything required to run the SAS server. 

## Dependancies
### Software

 1. Python 3+
 > You can check to see if you have Python by running the following command in the terminal: `python --version` You should see output such as: `Python X.X.X`. On machines with multple versions of Python, the command for Python may be `py` or `python3` rather. If Python is not installed, please visit [the official Python website](http://https://www.python.org/downloads/ "the official Python website") to download the free software.
 >> Python v3.9.1 was used during development

### Packages
These Python packages use pip for installation. To ensure you have pip, please run in the terminal: ``pip -V``. If it is an unknown command, try ``python -m pip -V``. If there is still an issue, make sure that pip has been installed with your version of Python.

 1. [Eventlet](https://pypi.org/project/eventlet/ "Eventlet")
 > This package may be installed with the command: ``pip install eventlet``
 >> v0.30.1 was used during development

 2. [Socketio](https://pypi.org/project/python-socketio/ "Socketio")
 > ``pip install python-socketio``
 >> v5.0.4 was used during development

 3. [Numpy](https://pypi.org/project/numpy/ "Numpy")
 > ``pip install numpy``
 >> v1.19.5 was used during development
 
## Starting the Server
Once all of the dependancies have been properly installed, the server may be started with the command: ``python server.py``. This will host the server on `localhost` port `8000`. Please ensure that this host:port is avaiable if there are issues starting the server. The output in the terminal will show ``wsgi starting up on http://0.0.0.0:8000`` upon a successful start to the server.

At this time, you may connect your socketio-enabled, network-attached radio clients to the SAS server. For an example of a client, refer to [cornet/socket_to_sas.py](https://github.com/vtwireless/SAS/blob/main/cornet/socket_to_sas.py "cornet/socket_to_sas.py")

## Files
### CBSD.py
This file holds the class that represents a node/CBSD that connects to the SAS server. 

### SASAlgorithms.py
This file holds all of the algorithms used by ``server.py``.

### SASREM.py
This file manages the radio environment map (REM) data gathered by the server.

### Simulator.py
This script simulates CBSDs connecting and interacting with the SAS Server. Primary, Secondary, and Malicious users may all be simulated. This allows for testing of SAS MU dection algorithms as well as SU scheduling algorithms. To use this, run this command in a new terminal window (not the terminal with the SAS server process running): ``python Simulator.py -s simulations/name_of_sim.json``. By defualt, the simulator will connect to localhost:8000. If your server is located elsewhere, use the flags ``-a`` and ``-p`` to provide the address and port information. When using this, ensure that the `isSimulating`  variable is enabled in ``server.py``.

> This does not need to execute for the server to properly work. This is for development/testing purposes.

### Server_WinnForum.py
This file contains the classes used for Object-Oriented programming. Most of the objects in this file are defined by the [WinnFourum/FCC standard](https://winnf.memberclicks.net/assets/CBRS/WINNF-TS-0016.pdf "WinnFourum/FCC standard"). These objects are used to ensure that the SAS server and client have consistent data structures in their socket messaging. If creating a custom client to this SAS, you may duplicate [cornet/Client_WinnForum.py](https://github.com/vtwireless/SAS/blob/main/cornet/Client_WinnForum.py "cornet/Client_WinnForum.py") to ensure that the objects are compatible between the SAS and client.
