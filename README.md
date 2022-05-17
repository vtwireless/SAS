# Spectrum Access System (SAS)
## What is this?
This is the code for the Virginia Tech Open Source SAS and Virginia Tech CORNET client. The role of the SAS is to allow
for remote and autonomous operation of the USRPs in Kelly Hall. The SAS is
to adhere to WinnForum and FCC regulations on SAS operations.

## File Structure
### Core
The Core/ folder contains everything required to launch the SAS Core
Server. This is the true SAS. It may have connections to N number of socketio
clients. Regardess of your institution, this contians the code that is of
primary interet for SAS researchers.

An example of starting up the SAS server server.py:
```python3 server.py```
### Cornet
The cornet/ folder contains everything required to launch the CORNET SAS
client. This connects to the SAS server, so ensure the sever is running
before attempting to launch this. If you are a Wireless@VT user with
CORNET access, this is how you can connect a Kelly Hall (or any other
network attached USRP) to the SAS.

An example of executing the CORNET SAS client socket_to_sas.py:
```python3 socket_to_sas.py -p 5000 -a "127.0.0.1" --sim "simulations/sim_one.json"```
**Note**: On CORNET there may be environment
issues with Python. Please use:
```grrun python3 socket_to_sas.py -p ... -a ... --sim ...```


## Environment Setup
This software needs GNURadio and UHD to be installed in the system, along with a few
other python libraries. For setting up the relevant python libraries, please refer
to the `requirements.txt [WIP]` file.

GNURadio: 3.8.5.0, UHD: 3.15.0.0-2build5

GNURadio and UHD Setup:
1. Uninstall any previous existing conflicting versions of GNURadio and UHD:
   * `sudo apt-get -y autoremove --purge gnuradio uhd-host`
   * `sudo apt-get update`
2. Check APT policy to see available gnuradio packages for installation:
    * `sudo apt-cache policy gnuradio`
3. The step above displays available gnuradio packages and their sources. Check if v3.8.5.0 is available.
    * If v3.8.5.0 is available, then install that specific version:
      * `sudo apt-get install gnuradio=3.8.5.0-0~gnuradio~focal-4`
      * NOTE: The name of the version of GNURadio (`~gnuradio~focal-4`) may be different in your case. Please substitute the name appropiately.
    * If v3.8.5.0 is not available, then update linux source repository:
      * `sudo add-apt-repository ppa:gnuradio/gnuradio-releases-3.8`
      * `sudo apt-get update`
      * Repeat from Step-2
4. GNURadio installation should now happen and might take some time. Once installation is complete, verify the installed version:
   * `gnuradio-config-info --version`
   * You should be able to see v3.8.5.0 installed. If, however, you see a different version installed, then:
     * Check APT policy cache again and see if you can see other versions of gnuradio:
       * `sudo apt-cache policy gnuradio`
     * Remove other version's repository manually, one-by-one. 
       * For v3.9.x.y, use command `sudo add-apt-repository --remove ppa:gnuradio/gnuradio-releases-3.9`
     * Remove the installed package:
       * `sudo apt-get -y autoremove --purge gnuradio`
     * At the end, do `sudo apt-get update` and check policy again to verify presence of v3.8.5.0.
     * Repeat from Step-2.
5. Setup UHD using `sudo apt-get install uhd-host=3.15.0.0-2build5` and wait for successful installation.
   * NOTE: Build name may be different in your case. Check with `sudo apt-cache policy uhd-host` and substitute accordingly.
6. Verify successful installation:
   * We can check it in a python terminal. Open a python terminal by entering `python3` in linux terminal. 
   * Inside the python terminal, execute following commands and verify that they are working:
     * `from gnuradio import uhd`
     * `uhd.find_devices()`
   * If we don't see errors at this stage, installation is complete and successful.

## Links
https://vtwireless.github.io/SAS/index.html


## Contacts
Contact Cameron Makin at cammakin8@vt.edu for questions
