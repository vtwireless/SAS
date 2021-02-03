# Spectrum Access System (SAS)
## What is this?
This is the code for the SAS. The role of the SAS is to allow for remote and autonomous operation of the USRPs in Kelly Hall. The SAS is to adhere to WinnForum and FCC regulations on SAS operations.

## File Structure (Needs to be updated as of 01/24/2021)
rx_usrp.py and tx_usrp.py are USRP Object files that work with the uhd_lib to control real USRPs. These files may be used individually to run Rx and Tx USRPs.

WinnForum.py is currently a file with Objects used for SAS-CBSD communications as defined by the WinnFourm (plus a few extra Virginia Tech (VT) Objects for research.   

All three of the above files are included in socket_rx.py and socket_tx.py. These two files are the ones you want to execute. And example of executing socket_tx.py: 
  ```./socket_tx.py -p 5000 -a "127.0.0.1" --device "192.168.40.206" --freq 915 --gain 0 --samplerate 1 --waveform "SINE" --sigamp 1```

## Contacts
Contact Cameron Makin at cammakin8@vt.edu for questions
