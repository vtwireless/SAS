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
 
## Using the Server
Once all of the dependancies have been properly installed, the server may be started with the command: ``python server.py``. This will host the server on `localhost` port `8000`. Please ensure that this host:port is avaiable if there are issues starting the server. The output in the terminal will show ``wsgi starting up on http://0.0.0.0:8000`` upon a successful start to the server.

At this time, you may connect your radio-attached clients to the SAS server.


