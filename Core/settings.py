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
DEVELOPMENT_DATABASE_URI = f'sqlite:///{SQLITE_FILE}'
PRODUCTION_DATABASE_URI = f"dialect+driver://{DATABASE['username']}:{DATABASE['password']}@{DATABASE['hostname']}:" \
                          f"{DATABASE['password']}/{DATABASE['db']}"

# Tables Settings
SECONDARY_USER_TABLE = 'secondaryUser'
