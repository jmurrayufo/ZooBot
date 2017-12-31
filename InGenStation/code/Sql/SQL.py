import asyncio
import csv
import hashlib
import json
import logging
import os
import os.path
import random
import re
import sqlite3
import time

from ..CustomLogging import Log

class SQL:

    __shared_state = {}


    def __init__(self, args=None):
        self.__dict__ = SQL.__shared_state
        if hasattr(self, 'initialized'):
            return
        self.args = args
        self.conn = None
        self.connected = False
        self.log = Log()
        self.initialized = True
        self.db_version = 1 # Used to check the version of the db


    def connect(self, db_name="hab.db"):
        self.log.info("Connect to db")
        if not self.connected:
            self.log.info("Not connected, open one")
            if not os.path.isfile(db_name):
                self.log.warning(f"Creating new db: {db_name}")
                self.conn = sqlite3.connect(db_name)
                self.c = self.conn.cursor()
                self.setup()
                self.conn.close()
            self.conn = sqlite3.connect(db_name)
            self.log.info("Connection established")
            self.conn.row_factory = sqlite3.Row
            self.c = self.conn.cursor()
            self.log.info("Cursor created, connection complete")
            self.connected = True


    def disconnect(self):
        self.log.info("Disconnect from db")
        if self.conn and self.connected:
            self.conn.close()
            self.conn = None
            self.connected = False


    def setup(self):
        self.log.info("Begining DB setup")
        if self.args.purpose in ['bug','test']:
            # Setup values for the bug hab
            sqlcmd = """
                CREATE TABLE settings(
                device TEXT,
                key TEXT,
                value TEXT,
                UNIQUE(device,key) ON CONFLICT REPLACE
                );"""
            self.c.execute(sqlcmd)

            sqlcmd = """
                CREATE TABLE devices(
                device TEXT);"""
            self.c.execute(sqlcmd)

            # Setup default values
            sqlcmd = """INSERT INTO settings VALUES ("heater0","max_on",60*60)"""
            self.c.execute(sqlcmd)

            sqlcmd = """INSERT INTO settings VALUES ("heater0","min_on",60)"""
            self.c.execute(sqlcmd)

            sqlcmd = """INSERT INTO settings VALUES ("heater0","max_off",60)"""
            self.c.execute(sqlcmd)

            sqlcmd = """INSERT INTO settings VALUES ("heater0","min_off",60)"""
            self.c.execute(sqlcmd)

            sqlcmd = """INSERT INTO settings VALUES ("heater0","temperature_limit_max",29)"""
            self.c.execute(sqlcmd)

            sqlcmd = """INSERT INTO settings VALUES ("heater0","temperature_limit_min",26)"""
            self.c.execute(sqlcmd)
            self.conn.commit()

            self.c.execute("PRAGMA journal_mode=WAL")
            self.conn.commit()

            self.c.execute("PRAGMA synchronous=1")
            self.conn.commit()

            self.c.execute(f"PRAGMA user_version = {self.db_version}")
            self.conn.commit()

    def get_setting(self, device, key):
            sqlcmd = """SELECT * FROM settings WHERE (device=? AND key=?)"""
            row = self.c.execute(sqlcmd,(device,key)).fetchone()

            if row == None:
                return None
            try:
                return int(row['value'])
            except ValueError:
                pass
            try:
                return float(row['value'])
            except ValueError:
                pass
            return row['value']

    def set_setting(self, device, key, value):
            sqlcmd = """INSERT INTO settings VALUES (?,?,?)"""
            self.c.execute(sqlcmd,(device,key,value))
            self.conn.commit()



