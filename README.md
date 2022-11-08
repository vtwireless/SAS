# Spectrum Access System (SAS)
## What is this?
This is the code for the Virginia Tech Open Source SAS and Virginia Tech CORNET client. The role of the SAS is to allow
for remote and autonomous operation of the USRPs in Kelly Hall. The SAS is
to adhere to WinnForum and FCC regulations on SAS operations.

## Environment Setup
This software needs GNURadio and UHD to be installed in the system, along with a few
other python libraries. For setting up the relevant python libraries, please refer
to the `requirements.txt [WIP]` file.

GNURadio: **3.8.5.0**, UHD: **3.15.0.0-2build5**

## GNURadio and UHD Setup:
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

## Python Dev Environment Setup
Once gnuradio and uhd-host packages are successfully installed, we can move on to setting up the python environment. 
This application needs **python 3.8**.
1. Verify that python3.X is installed in your system.
   * `which python3` [or if you have a specific version installed, then `which python3.8`]
2. Create a virtual environment at the base of the repository.
   * Make sure you are at the root or base of the repository. You can check by confirming current path with `pwd`.
   * Install `virtualenv`, if not already done: `python3 -m pip install virtualenv`
   * Create the environment: `virtualenv lib -p $(which python3)`
3. Activate the environment and install required packages:
   * Activate environment: `source lib/bin/activate`.
   * Install packages: `pip install -r requirements.txt`.
   
## FrontEnd Dev Environment Setup
1. Install nodejs and npm.
   * `sudo apt-get install nodejs` and `sudo apt-get install npm`.
   * Currently, we are using nodejs v16.17.0 and npm v8.15.0
2. Install Angular 8.2.0 \[as suggested in the package.json\].
   * `sudo npm install -g @angular/cli@8.2.0`
3. Install the rest of the dependencies. While the 2 commands above can be run from
anywhere, this specific one needs to be run from the location where the **package.json**
resides, which should be ./.../SAS/FrontEnd
   * `npm install`

## Database Setup
### Install phpmyadmin
1. Install the software using the following commands: 
   1. `sudo apt update`.
   2. `sudo apt install phpmyadmin php-mbstring php-zip php-gd php-json php-curl`
   3. `sudo phpenmod mbstring`
   4. `sudo systemctl restart apache2`

### Install Mariadb
https://www.digitalocean.com/community/tutorials/how-to-install-mariadb-on-ubuntu-20-04
1. Install the database:
   1. `sudo apt update` 
   2. `sudo apt install mariadb-server` 
   3. `sudo systemctl start mariadb.service`
2. Configure database:
   1. `sudo mysql_secure_installation`
   2. Follow the prompt and setup root password. Root password can be modified in the following way:
      1. `sudo mysql`
      2. `ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';`
      3. `exit`.
      4. Subsequent logins for root should now be available with password: `mysql -u root -p`.
   3. Create a database: `CREATE DATABASE spectrumGrant;`.
3. Create tables using the `.sql` file available in `database_API` folder.
   1. In the folder's location, execute `mysql -u root -p < spectrumGrant\ v1.0.sql`.
   2. Verify that the tables are created in the database.

### Setup Database files
We need to host database API files on APACHE. To do this, move the `.php` files from 
`database_API` and place them inside `SASAPI` folder. This folder needs to be created
inside `\var\www\html\ `.

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


## Links
https://vtwireless.github.io/SAS/index.html


## Contacts
Contact Cameron Makin at cammakin8@vt.edu for questions
