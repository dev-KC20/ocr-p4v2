#! /usr/bin/env python
# coding: utf-8
"""all database meta-operations.


"""
from tinydb import TinyDB  #, Query

from utils.constants import DB_LOCATION

class Database:

    def __init__(self):
        self.__db = TinyDB(DB_LOCATION, sort_keys=True)

    def __open_table(self, table):    
        __table = self.__db.table(table)
        return __table

    def get_table_all(self, table):
        records = self.__open_table(table).all()
        return records
    
    def set_table_all(self, table, dict_records):
        self.__open_table(table).insert(dict_records)
        
    
    def get_table_id(self, table, record_id=None):
        if record_id is not None:
            record = self.__open_table(table).get(table.get_id == record_id)
        return record
    
            

    


    

