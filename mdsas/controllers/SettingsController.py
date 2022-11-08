import sqlalchemy as db
from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult

from algorithms.SASAlgorithms import SASAlgorithms
from settings import settings


class SettingsController:
    SETTINGS = None

    def __init__(self, metadata, engine, connection, algorithms):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms: SASAlgorithms = algorithms

        self._set_settings_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def _set_settings_table(self):
        self.SETTINGS = db.Table(
            settings.SETTINGS_TABLE, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )
        self.create_sas_settings()

    def get_settings_table(self):
        return self.SETTINGS

    def get_sas_settings(self, algorithm=None):
        if not algorithm:
            query = select([self.SETTINGS])
        else:
            query = select([self.SETTINGS]).where(
                self.SETTINGS.columns.algorithm == algorithm
            )

        try:
            result = self._execute_query(query)[0]
            message = f"GRANT: {result['algorithm']}, " \
                      f"HB: {str(result['heartbeatInterval'])}, " \
                      f"REM: {result['REMAlgorithm']}"
            print(message)

        except Exception as err:
            raise Exception(str(err))

    def set_algorithm_settings(self, result):
        self.algorithms.setGrantAlgorithm(result["algorithm"])
        self.algorithms.setHeartbeatInterval(result["heartbeatInterval"])
        self.algorithms.setREMAlgorithm(result["REMAlgorithm"])

    def create_sas_settings(self, data=None):
        if not data:
            data = {
                'algorithm': 'DEFAULT',
                'heartbeatInterval': self.algorithms.defaultHeartbeatInterval,
                'REMAlgorithm': 'DEFAULT'
            }

        try:
            self.CONNECTION.execute(self.SETTINGS.insert(), [data])
            self.set_algorithm_settings(data)
        except Exception as err:
            raise Exception(str(err))

    def update_sas_settings(self, data):
        updateQuery = update(self.SETTINGS)\
            .where(self.SETTINGS.columns.algorithm == data.algorithm)\
            .values(
                heartbeatInterval=data['heartbeatInterval'],
                REMAlgorithm=data['REMAlgorithm']
            )
        ResultProxy = self.CONNECTION.execute(updateQuery)

        self.set_algorithm_settings(data)
        self.get_sas_settings()
