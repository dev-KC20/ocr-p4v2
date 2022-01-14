#! /usr/bin/env python
# coding: utf-8
"""All database meta-operations."""
from tinydb import TinyDB, Query

from utils.constants import DB_LOCATION, DB_TABLE_TOURNAMENT, DB_TABLE_PLAYER


class Database:
    """Initiate the DB connection based on DB_LOCATION json file."""

    def __init__(self):
        """Database class init to connect to the DB file."""
        try:
            self.__db = TinyDB(DB_LOCATION, sort_keys=True)
        except FileNotFoundError:
            print("Avez-vous bien installé un répertoire data pour y loger le fichier json de la base ?")

    def __open_table(self, table):
        """Open the table in parm."""
        __table = self.__db.table(table)
        return __table

    def get_table_all(self, table):
        """Get all the records from table in parm."""
        records = self.__open_table(table).all()
        return records

    def truncate_table(self, table):
        """Remove all the records from table in parm."""
        self.__open_table(table).truncate()

    def set_table_all(self, table, dict_records):
        """Insert by batch of records into table in parm."""
        self.__open_table(table).insert(dict_records)

    def set_table(self, table, dict_records, id_doc=None):
        """Insert records into & update the table id of table in parm."""
        if id_doc is None:
            insert_result = self.__open_table(table).insert(dict_records)
            if table == DB_TABLE_PLAYER:
                self.__open_table(table).update({"player_id": insert_result}, doc_ids=[insert_result])
            if table == DB_TABLE_TOURNAMENT:
                self.__open_table(table).update({"tournament_id": insert_result}, doc_ids=[insert_result])
        else:
            self.__open_table(table).update(dict_records, doc_ids=[id_doc])

    def get_table_id(self, table, record_id=None):
        """Get the record from the id of record of table in parm."""
        if record_id is not None:
            record = self.__open_table(table).get(table.get_tournament_id == record_id)
        return record

    def search_table_single(self, table, attribut, value):
        """Get the record that match value of the attribut of table in parm."""
        request = Query()
        # filter the records
        return self.__open_table(table).search(request[attribut] == value)
