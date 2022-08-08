import os
import sys

from sqlalchemy import MetaData

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grants_schema
import nodes_schema
import pudetections_schema
import settings_schema
import users_schema


class Schemas:
    def __init__(self, metadata: MetaData):
        self._metadata = metadata

    def create_tables(self):
        self.__get_user_table()
        self.__get_node_table()
        self.__get_grant_table()
        self.__get_puDetections()
        self.__get_settings()

    def __get_settings(self):
        settings_schema.set_schema(self._metadata)
        
    def __get_user_table(self):
        users_schema.set_schema(self._metadata)

    def __get_node_table(self):
        nodes_schema.set_schema(self._metadata)

    def __get_grant_table(self):
        grants_schema.set_schema(self._metadata)

    def __get_puDetections(self):
        pudetections_schema.set_schema(self._metadata)
