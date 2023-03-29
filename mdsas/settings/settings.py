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
DEVELOPMENT_DATABASE_URI = f'sqlite:///{SQLITE_FILE}?check_same_thread=False'
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

# App Settings
APP_NAME = 'swift_ascent'
