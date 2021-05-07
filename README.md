# Spectrum Access System (SAS)
## What is this?
This is the code for the SAS and a client. The role of the SAS is to allow
for remote and autonomous operation of the USRPs in Kelly Hall. The SAS is
to adhere to WinnForum and FCC regulations on SAS operations.

## File Structure (Needs to be updated as of 01/24/2021)
The Core/ folder contains everything required to launch the SAS Core
Server. This is the true SAS. It may have connections to N number of
clients. Regardess of your institution, this contians the code that is of
primary interet for SAS researchers.

An example of starting up the SAS server server.py:
```python3 server.py```

The cornet/ folder contains everything required to launch the CORNET SAS
client. This connects to the SAS server, so ensure the sever is running
before attempting to launch this. If you are a Wireless@VT user with
CORNET access, this is how you can connect a Kelly Hall (or any other
network attached USRP) to the SAS.

An example of executing the CORNET SAS client socket_to_sas.py:
```python3 socket_to_sas.py -p 5000 -a "127.0.0.1" --sim
"simulations/sim_one.json"```
*Note: On CORNET there may be environment
issues with Python. Please use:
```grrun python3 socket_to_sas.py -p ... -a ... --sim ...```


## Links
https://vtwireless.github.io/SAS/index.html


## Contacts
Contact Cameron Makin at cammakin8@vt.edu for questions
