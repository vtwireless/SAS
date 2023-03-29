import os
import sys

from sqlalchemy import MetaData

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grants_schema
import nodes_schema
import pudetections_schema
import settings_schema
import users_schema
import tierclass_schema
import tierassignment_schema
import regionschedule_schema
import inquirylog_schema
import basestation_schema


class Schemas:
    def __init__(self, metadata: MetaData):
        self._metadata = metadata

    def create_tables(self):
        self.__get_settings()
        self.__get_user_table()
        self.__get_node_table()
        self.__get_grant_table()
        self.__get_puDetections()
        self.__get_tierclass_table()
        # self.__get_tierassignment_table()
        self.__get_regionschedule_table()
        self.__get_inquirylog_table()
        self.__get_basestation_table()

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

    def __get_tierclass_table(self):
        tierclass_schema.set_schema(self._metadata)

    def __get_tierassignment_table(self):
        tierassignment_schema.set_schema(self._metadata)

    def __get_regionschedule_table(self):
        regionschedule_schema.set_schema(self._metadata)

    def __get_inquirylog_table(self):
        inquirylog_schema.set_schema(self._metadata)

    def __get_basestation_table(self):
        basestation_schema.set_schema(self._metadata)
