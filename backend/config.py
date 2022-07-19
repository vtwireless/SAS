import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sas_app.db'


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
