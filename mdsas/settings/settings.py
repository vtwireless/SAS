# Environment Settings
ENVIRONMENT = 'DEVELOPMENT'
ADMIN_EMAIL = 'admin'
ADMIN_PWD = 'admin'

# Database Settings
DATABASE = dict(
    username='',
    password='',
    hostname='',
    port='',
    db=''
)
SQLITE_FILE = 'mdsas.db'
DEVELOPMENT_DATABASE_URI = f'sqlite:///db/{SQLITE_FILE}?check_same_thread=False'
PRODUCTION_DATABASE_URI = f"dialect+driver://{DATABASE['username']}:{DATABASE['password']}@{DATABASE['hostname']}:" \
                          f"{DATABASE['password']}/{DATABASE['db']}"

# Tables Settings
SETTINGS_TABLE = 'settings'
SECONDARY_USER_TABLE = 'secondaryUser'
CBSD_TABLE = 'node'
GRANT_TABLE = 'grants'
PUDETECTIONS = 'pudetections'
TIERCLASS = 'tierclass'
TIERASSIGNMENT = 'tierassignment'
REGIONSCHEDULE = 'regionSchedule'
INQUIRYLOG = 'inquirylogs'
GRANTREQUEST = 'grantrequest'

BASESTATION_TABLE = 'basestations'

# Simulator Settings
SIM_SETTINGS_FILE = "db/sim_settings.json"
INCLUSION_ZONE_RADIUS = 5000
EXCLUSION_ZONE_RADIUS = 500
EXCLUSION_ZONE_RADIUS_STEP = 500
SIMULATION_COUNT = 1
BS_COUNT = 33
BS_UE_RADIUS = [1, 1000]
INR_THRESHOLD = {
    "rain": -12, "default": -8.5
}

# App Settings
APP_NAME = 'swift_ascent'
