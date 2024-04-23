# Multi-Dimensional Spectrum Access System (SAS)
## What is this?
This is the code for the Virginia Tech Open Source MD-SAS. The role of the SAS is to allow for remote and autonomous 
operation of the USRPs in Kelly Hall. The SAS is to adhere to WinnForum and FCC regulations on SAS operations.

## Python Dev Environment Setup
This application needs atleast **python 3.8**.

Set the python version to **less than or equal to version 3.9** for the required packages to be installed as part of backend setup without any issue. 

1. Verify that python3.X is installed in your system.
   * `which python3` [or if you have a specific version installed, then `which python3.8`]
2. Create a virtual environment at the base of the repository.
   * Make sure you are at the root or base of the repository. You can check by confirming current path with `pwd`.
   * Install `virtualenv`, if not already done: `python3 -m pip install virtualenv`
   * Create the environment: `virtualenv lib -p $(which python3)`
3. Activate the environment and install required packages:
   * Activate environment: `source lib/bin/activate`.
   * Install packages: `pip install -r requirements.txt`.
4. Follow the **steps.txt** file for HTTPS SSL Certificate Generation and Installation
NOTE: We can comment on the **ssl_context part** for the setup to run locally.


## SQLITE DB Environment Setup

1. Install **SQlite** to set up the database locally.
2. You can execute **seed_rendered.py in tests dir** to get some seed data into our database.  
   
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

## Repository Structure Structure
* ### mdsas directory
This directory contains the main source code for MD-SAS. To run the MD-SAS server, one needs to run the `rest_server.py`
file using `python rest_server.py` command. Related configuration settings for MD-SAS can be found inside the 
`settings/settings.py` file. At the time of creating this document, the MD-SAS server starts at `port 8000` in
**HTTPS mode**. HTTPS certificates can be found in the `certs` directory and can be installed on systems that intend to
access this service.

* ### FrontEnd directory
This directory contains an angular frontend to view/access the features of the MD-SAS. While MD-SAS can be directly
accessed via REST APIs, this frontend provides an easier way to view/access MD-SAS features. To start the frontend, 
Use this command: **$env:NODE_OPTIONS="--openssl-legacy-provider"** before running `npm run start` Or: **use node version <=16**. 
One needs to simply execute `npm run start` in a terminal. At the time of creating this document, the frontend server is
accessible over `port 4200`.

* ### archive directory
This directory contains legacy code for quick access and review. It will be removed in the future and is only meant to
act as a reference point for developmental work.

## Contacts
Contact Saurav Kumar at sauravk3@vt.edu for questions.
